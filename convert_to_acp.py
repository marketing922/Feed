import pandas as pd
import re
import json
import os

# --- 0. Charger les deux sources et fusionner ---
# CSV = source initiale (Google Shopping), XLSX = export frais (prioritaire)
df = pd.read_csv("Intégration ACP - Feuille 1.csv", dtype=str, keep_default_na=False)

xlsx_file = "export-variants-2026-03-12.xlsx"
if os.path.exists(xlsx_file):
    dx = pd.read_excel(xlsx_file, dtype=str, keep_default_na=False)
    dx["id"] = dx["id"].str.strip()
    df["id"] = df["id"].str.strip()

    # Indexer le XLSX par id pour lookups rapides
    dx_idx = dx.set_index("id")

    # a) Ajouter les 94 nouveaux produits du XLSX absents du CSV
    new_ids = set(dx["id"]) - set(df["id"])
    if new_ids:
        new_rows = dx[dx["id"].isin(new_ids)].copy()
        # Mapper les colonnes XLSX -> CSV
        new_rows.rename(columns={
            "url": "link",
            "image_link": "image link",
            "additional_image_link": "additional image link",
            "item_group_id": "item group id",
        }, inplace=True)
        # Ajouter les colonnes CSV manquantes avec des valeurs par defaut
        for col in df.columns:
            if col not in new_rows.columns:
                new_rows[col] = ""
        # Remplir des champs par defaut pour les nouveaux produits
        new_rows["brand"] = "Laboratoire Calebasse"
        new_rows["condition"] = "new"
        # Mapper availability XLSX -> CSV format
        avail_map_xlsx = {"AVAILABLE": "in_stock", "OUT_OF_STOCK": "out_of_stock", "AVAILABLE_SOON": "preorder"}
        new_rows["availability"] = new_rows["availability"].map(avail_map_xlsx).fillna("out_of_stock")
        df = pd.concat([df, new_rows[df.columns]], ignore_index=True)
        print(f"  + {len(new_ids)} nouveaux produits ajoutes depuis le XLSX")

    # b) Retirer les 32 produits absents du XLSX
    removed_ids = set(df["id"]) - set(dx["id"])
    if removed_ids:
        df = df[~df["id"].isin(removed_ids)].reset_index(drop=True)
        print(f"  - {len(removed_ids)} produits retires (absents du XLSX)")

    # c) Mettre a jour les champs depuis le XLSX pour les IDs communs
    common_mask = df["id"].isin(dx_idx.index)
    common_ids = df.loc[common_mask, "id"]

    # Availability (254 changements)
    avail_map_xlsx = {"AVAILABLE": "in_stock", "OUT_OF_STOCK": "out_of_stock", "AVAILABLE_SOON": "preorder"}
    new_avail = common_ids.map(lambda i: avail_map_xlsx.get(dx_idx.loc[i, "availability"], "out_of_stock"))
    changed_avail = (df.loc[common_mask, "availability"] != new_avail).sum()
    df.loc[common_mask, "availability"] = new_avail.values
    print(f"  ~ {changed_avail} disponibilites mises a jour")

    # Titres (prendre le XLSX comme reference)
    new_titles = common_ids.map(lambda i: dx_idx.loc[i, "title"].strip().rstrip("\n"))
    changed_titles = (df.loc[common_mask, "title"] != new_titles).sum()
    df.loc[common_mask, "title"] = new_titles.values
    print(f"  ~ {changed_titles} titres mis a jour")

    # Images (146 changements)
    new_imgs = common_ids.map(lambda i: dx_idx.loc[i, "image_link"].strip() if dx_idx.loc[i, "image_link"] else "")
    changed_imgs = ((new_imgs != "") & (df.loc[common_mask, "image link"] != new_imgs)).sum()
    df.loc[common_mask, "image link"] = new_imgs.where(new_imgs != "", df.loc[common_mask, "image link"]).values
    print(f"  ~ {changed_imgs} images mises a jour")

    # Additional images
    new_addimgs = common_ids.map(lambda i: dx_idx.loc[i, "additional_image_link"].strip() if dx_idx.loc[i, "additional_image_link"] else "")
    df.loc[common_mask, "additional image link"] = new_addimgs.where(
        new_addimgs != "", df.loc[common_mask, "additional image link"]
    ).values

    # URLs (17 changements)
    new_urls = common_ids.map(lambda i: dx_idx.loc[i, "url"].strip() if dx_idx.loc[i, "url"] else "")
    changed_urls = ((new_urls != "") & (df.loc[common_mask, "link"] != new_urls)).sum()
    df.loc[common_mask, "link"] = new_urls.where(new_urls != "", df.loc[common_mask, "link"]).values
    print(f"  ~ {changed_urls} URLs mises a jour")

    # item_group_id (13 changements)
    new_grps = common_ids.map(lambda i: dx_idx.loc[i, "item_group_id"].strip() if dx_idx.loc[i, "item_group_id"] else "")
    df.loc[common_mask, "item group id"] = new_grps.where(new_grps != "", df.loc[common_mask, "item group id"]).values

    # Shipping weight -> poids (nouveau champ du XLSX)
    new_weights = common_ids.map(lambda i: dx_idx.loc[i, "shipping_weight"].strip() if dx_idx.loc[i, "shipping_weight"] else "")
    df.loc[common_mask, "_shipping_weight"] = new_weights.values
    # Aussi pour les nouveaux produits
    if "_shipping_weight" not in df.columns:
        df["_shipping_weight"] = ""
    new_prod_mask = df["id"].isin(new_ids) if new_ids else pd.Series([False]*len(df))
    if new_prod_mask.any():
        df.loc[new_prod_mask, "_shipping_weight"] = df.loc[new_prod_mask, "id"].map(
            lambda i: dx_idx.loc[i, "shipping_weight"].strip() if i in dx_idx.index and dx_idx.loc[i, "shipping_weight"] else ""
        ).values

    # rich_text_description (exploiter pour enrichir description)
    def extract_rich_desc(html):
        """Extraire les bullet points du rich_text_description HTML"""
        if not html or html == "<ul></ul>":
            return ""
        # Extraire le texte des <li>
        items = re.findall(r"<li>(.*?)</li>", html, re.DOTALL)
        if items:
            # Nettoyer les tags HTML restants
            cleaned = [re.sub(r"<[^>]+>", "", item).strip() for item in items]
            return " | ".join(cleaned)
        return ""

    rich_descs = common_ids.map(lambda i: extract_rich_desc(dx_idx.loc[i, "rich_text_description"]) if dx_idx.loc[i, "rich_text_description"] else "")
    # Ajouter comme colonne temporaire pour enrichir la description plus tard
    df.loc[common_mask, "_rich_desc"] = rich_descs.values
    if "_rich_desc" not in df.columns:
        df["_rich_desc"] = ""

    # category du XLSX
    cats = common_ids.map(lambda i: dx_idx.loc[i, "category"].strip() if dx_idx.loc[i, "category"] else "")
    df.loc[common_mask, "_xlsx_category"] = cats.values
    if "_xlsx_category" not in df.columns:
        df["_xlsx_category"] = ""

    print(f"  = Fusion XLSX terminee")
else:
    print("  ! XLSX non trouve, utilisation du CSV seul")
    df["_shipping_weight"] = ""
    df["_rich_desc"] = ""
    df["_xlsx_category"] = ""

# --- 1. Renommer les colonnes Google → ACP ---
rename_map = {
    "id": "item_id",
    "link": "url",
    "image link": "image_url",
    "additional image link": "additional_image_urls",
    "item group id": "group_id",
    "product_type": "product_category",
    "sale price": "sale_price",
    "sale price effective date": "sale_price_effective_date",
    "availability date": "availability_date",
    "expiration date": "expiration_date",
    "age group": "age_group",
    "size system": "size_system",
    "unit pricing measure": "unit_pricing_measure",
    "unit pricing base measure": "unit_pricing_base_measure",
}
df.rename(columns=rename_map, inplace=True)

# --- 1b. Enrichir la description avec rich_text_description ---
if "_rich_desc" in df.columns:
    mask = (df["description"] == "") & (df["_rich_desc"] != "")
    df.loc[mask, "description"] = df.loc[mask, "_rich_desc"]
    # Pour les produits avec description existante, ajouter les highlights
    mask2 = (df["description"] != "") & (df["_rich_desc"] != "")
    df.loc[mask2, "description"] = df.loc[mask2, "description"] + " — " + df.loc[mask2, "_rich_desc"]

# --- 1c. Utiliser la category XLSX comme fallback pour product_type ---
if "_xlsx_category" in df.columns:
    mask = (df.get("product_type", pd.Series([""] * len(df))) == "") & (df["_xlsx_category"] != "")
    if "product_type" in df.columns:
        df.loc[mask, "product_type"] = df.loc[mask, "_xlsx_category"]

# --- 2. Supprimer les colonnes Google-only (pas dans ACP) ---
cols_to_drop = [
    "mobile link", "identifier exists", "product highlight",
    "product detail", "pattern", "is bundle",
    "energy efficiency class", "min energy efficiency class",
    "sell on google quantity", "google_product_category",
    "adult", "size type",
]
df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

# --- 3. Corriger le format des prix: "9,40 EUR" -> "9.40 EUR" ---
def fix_price(val):
    if not val or val.strip() == "":
        return ""
    return re.sub(r"(\d+),(\d+)", r"\1.\2", val)

df["price"] = df["price"].apply(fix_price)
if "sale_price" in df.columns:
    df["sale_price"] = df["sale_price"].apply(fix_price)

# --- 4. Colonnes REQUIRED ACP ---

# OpenAI Flags
df["is_eligible_search"] = "true"
df["is_eligible_checkout"] = "true"

# Merchant Info
df["seller_name"] = "Laboratoire Calebasse"
df["seller_url"] = "https://calebasse.com"
df["seller_privacy_policy"] = "https://calebasse.com/politique-confidentialite"
df["seller_tos"] = "https://calebasse.com/cgv"

# Geo
df["target_countries"] = "FR"
df["store_country"] = "FR"

# Variations - determiner via group_id
group_counts = df[df["group_id"] != ""].groupby("group_id")["item_id"].count()
multi_variant_groups = set(group_counts[group_counts > 1].index)
df["listing_has_variations"] = df["group_id"].apply(
    lambda gid: "true" if gid in multi_variant_groups else "false"
)

# Return policy (required)
df["return_policy"] = "https://calebasse.com/cgv"

# --- 5. Gerer sale_price_effective_date -> split ---
if "sale_price_effective_date" in df.columns:
    def split_date(val, idx):
        if not val or "/" not in val:
            return ""
        parts = val.split("/")
        return parts[idx].strip() if idx < len(parts) else ""

    df["sale_price_start_date"] = df["sale_price_effective_date"].apply(lambda v: split_date(v, 0))
    df["sale_price_end_date"] = df["sale_price_effective_date"].apply(lambda v: split_date(v, 1))
    df.drop(columns=["sale_price_effective_date"], inplace=True)

# --- 6. Construire variant_dict a partir du titre ---
# Extraire le format (Petit Sachet, Grand Sachet, poudre concentree, gelules) et le poids
def build_variant_dict(title):
    variant = {}
    # Detecter le format du produit
    title_lower = title.lower()
    if "poudre concentr" in title_lower:
        variant["format"] = "Poudre concentree"
    elif "gelules" in title_lower or "gélules" in title_lower:
        variant["format"] = "Gelules"
    elif "grand sachet" in title_lower:
        variant["format"] = "Grand Sachet"
    elif "petit sachet" in title_lower:
        variant["format"] = "Petit Sachet"
    elif "sachets" in title_lower or "sachet" in title_lower:
        variant["format"] = "Sachet"

    # Extraire le poids
    weight_match = re.search(r"(\d+\s*[gG](?:r)?)\b", title)
    if weight_match:
        variant["poids"] = weight_match.group(1).strip()

    if variant:
        return json.dumps(variant, ensure_ascii=False)
    return ""

df["variant_dict"] = df["title"].apply(build_variant_dict)

# --- 7. Construire item_group_title (titre du groupe sans la variante) ---
def build_group_title(title):
    # Retirer la partie apres le tiret qui contient le format/poids
    # Ex: "Armoise argienne - Ai ye - 1 Petit Sachet plante 100g" -> "Armoise argienne - Ai ye"
    parts = title.split(" - ")
    if len(parts) >= 2:
        # Garder les 2 premieres parties (nom FR - nom CN)
        return " - ".join(parts[:2]).strip()
    return title

df["item_group_title"] = df["title"].apply(build_group_title)

# --- 8. Custom variants pour le format et le poids ---
def get_custom_variant_format(title):
    title_lower = title.lower()
    if "poudre concentr" in title_lower:
        return "Poudre concentree"
    elif "gelules" in title_lower or "gélules" in title_lower:
        return "Gelules"
    elif "grand sachet" in title_lower:
        return "Grand Sachet"
    elif "petit sachet" in title_lower:
        return "Petit Sachet"
    elif "sachets" in title_lower or "sachet" in title_lower:
        return "Sachet"
    elif "flacon" in title_lower:
        return "Flacon"
    return ""

def get_weight_from_title(title):
    match = re.search(r"(\d+)\s*g\b", title, re.IGNORECASE)
    return match.group(1) + "g" if match else ""

df["custom_variant1_category"] = "Format"
df["custom_variant1_option"] = df["title"].apply(get_custom_variant_format)
df["custom_variant2_category"] = "Poids"
df["custom_variant2_option"] = df["title"].apply(get_weight_from_title)
df["custom_variant3_category"] = ""
df["custom_variant3_option"] = ""

# --- 9. Colonnes optionnelles avec valeurs par defaut ---

# Fulfillment
df["shipping"] = "FR:::0.00 EUR:2-5 days"  # Livraison gratuite a partir de 39 EUR
df["is_digital"] = "false"

# Returns
df["accepts_returns"] = "true"
df["return_deadline_in_days"] = "14"
df["accepts_exchanges"] = "true"

# Compliance - Avertissements standard depuis les fiches produit calebasse.com
warning_standard = (
    "Complement alimentaire deconseille aux enfants de moins de 12 ans. "
    "Deconseille aux femmes enceintes et allaitantes. "
    "Ne peut se substituer a une alimentation diversifiee et un mode de vie sain. "
    "Ne pas depasser la dose journaliere recommandee. "
    "Conserver au sec, a l'abri de la lumiere et de l'humidite. "
    "Tenir hors de portee des enfants."
)
df["warning"] = warning_standard
df["age_restriction"] = "12"

# Media (colonnes vides si pas de donnees)
if "video_url" not in df.columns:
    df["video_url"] = ""
if "model_3d_url" not in df.columns:
    df["model_3d_url"] = ""

# Item dimensions (vides - pas applicable pour les plantes)
for col in ["dimensions", "length", "width", "height", "dimensions_unit"]:
    if col not in df.columns:
        df[col] = ""

# Poids : priorite au titre, fallback sur shipping_weight du XLSX
df["weight"] = df["title"].apply(get_weight_from_title)
# Fallback: utiliser shipping_weight du XLSX si pas de poids dans le titre
if "_shipping_weight" in df.columns:
    no_weight = df["weight"] == ""
    has_xlsx_weight = df["_shipping_weight"] != ""
    df.loc[no_weight & has_xlsx_weight, "weight"] = df.loc[no_weight & has_xlsx_weight, "_shipping_weight"].apply(
        lambda w: str(int(float(w))) + "g" if w else ""
    )
df["item_weight_unit"] = df["weight"].apply(lambda w: "g" if w else "")
# Convertir weight au bon format (juste le nombre)
df["weight"] = df["weight"].apply(lambda w: w.replace("g", "") if w else "")

# Prix et promos
if "pricing_trend" not in df.columns:
    df["pricing_trend"] = ""
if "unit_pricing_measure" not in df.columns:
    df["unit_pricing_measure"] = ""
if "unit_pricing_base_measure" not in df.columns:
    df["unit_pricing_base_measure"] = ""

# Availability
if "pickup_method" not in df.columns:
    df["pickup_method"] = "in_store"  # Retrait en boutique possible (15 rue de la Vistule)
if "pickup_sla" not in df.columns:
    df["pickup_sla"] = ""

# Marketplace
df["marketplace_seller"] = ""
df["offer_id"] = ""

# Performance signals
df["popularity_score"] = ""
df["return_rate"] = ""

# Reviews & Q&A
df["review_count"] = ""
df["star_rating"] = ""
df["store_review_count"] = ""
df["store_star_rating"] = ""

# Q&A - FAQ generique du site calebasse.com applicable a tous les produits
qa_list = [
    {"q": "Comment preparer et utiliser les plantes ?",
     "a": "Plantes entieres : decoction 20 min, boire apres les repas. Gelules : 6 par jour. Poudre concentree : diluer dans de l'eau chaude. Poudre moulue : faire bouillir 10 min."},
    {"q": "Combien de temps dure un traitement ?",
     "a": "Un traitement de 3 semaines est necessaire pour soulager les maux legers. Les premiers effets se ressentent generalement apres 3 semaines."},
    {"q": "Combien de temps dure une boite de 100 gelules ?",
     "a": "Environ 15 jours a raison de 6 gelules par jour."},
    {"q": "Peut-on utiliser les plantes pendant la grossesse ou l'allaitement ?",
     "a": "Verifiez la section Precautions d'emploi sur la fiche produit. En cas de doute, consultez votre praticien."},
    {"q": "Quelle est la quantite maximale par jour ?",
     "a": "En general, 13 g de poudre concentree ou 200 g de plantes entieres maximum par jour."},
    {"q": "Les gelules sont-elles d'origine naturelle ?",
     "a": "Oui, nos gelules sont en pullulane, une matiere naturelle sans risques pour la sante, sans transformation chimique et non allergene."},
    {"q": "D'ou proviennent les plantes ?",
     "a": "Toutes nos plantes proviennent de Chine ou elles sont cultivees avec le plus grand soin dans leurs regions de predilection, avec des controles qualite a l'export, l'import et en laboratoire."},
    {"q": "Combien de temps peut-on conserver les produits ?",
     "a": "Nos produits peuvent etre consommes plusieurs annees apres leur achat, a condition de les conserver a l'abri de l'humidite et du soleil."},
    {"q": "Les emballages sont-ils recyclables ?",
     "a": "Oui, les sachets en papier kraft et les flacons en plastique HDPE sont recyclables. Vous pouvez aussi rapporter les flacons vides en boutique ou par courrier."},
    {"q": "Quels sont les modes de livraison ?",
     "a": "Colissimo (48h), Chronopost (24h), points relais (48h), ou retrait en boutique au 15 rue de la Vistule, Paris 13. Livraison gratuite en point relais des 39 EUR."},
]
df["q_and_a"] = json.dumps(qa_list, ensure_ascii=False)

df["reviews"] = ""

# Related products - charger depuis le fichier JSON si disponible
import os
related_file = "related_products.json"
if os.path.exists(related_file):
    with open(related_file, "r", encoding="utf-8") as f:
        related_map = json.load(f)
    # Pour chaque produit, trouver les related products via son group_id
    def get_related(group_id):
        if group_id in related_map:
            return ",".join(related_map[group_id])
        return ""
    df["related_product_id"] = df["group_id"].apply(get_related)
    df["relationship_type"] = df["related_product_id"].apply(
        lambda r: "often_bought_with" if r else ""
    )
    related_count = (df["related_product_id"] != "").sum()
    print(f"  - Related products charges pour {related_count} produits")
else:
    df["related_product_id"] = ""
    df["relationship_type"] = ""
    print("  - related_products.json non trouve, related_product_id vide")

# Geo overrides
df["geo_price"] = ""
df["geo_availability"] = ""

# --- 10. Ordonner les 77 colonnes selon la spec ACP ---
all_columns_ordered = [
    # OpenAI Flags (2)
    "is_eligible_search",
    "is_eligible_checkout",
    # Basic Product Data (6)
    "item_id",
    "gtin",
    "mpn",
    "title",
    "description",
    "url",
    # Item Information (13)
    "brand",
    "condition",
    "product_category",
    "material",
    "dimensions",
    "length",
    "width",
    "height",
    "dimensions_unit",
    "weight",
    "item_weight_unit",
    "age_group",
    # Media (4)
    "image_url",
    "additional_image_urls",
    "video_url",
    "model_3d_url",
    # Price & Promotions (6)
    "price",
    "sale_price",
    "sale_price_start_date",
    "sale_price_end_date",
    "unit_pricing_measure",
    "pricing_trend",
    # Availability & Inventory (5)
    "availability",
    "availability_date",
    "expiration_date",
    "pickup_method",
    "pickup_sla",
    # Variants (14)
    "group_id",
    "listing_has_variations",
    "variant_dict",
    "item_group_title",
    "color",
    "size",
    "size_system",
    "gender",
    "offer_id",
    "custom_variant1_category",
    "custom_variant1_option",
    "custom_variant2_category",
    "custom_variant2_option",
    "custom_variant3_category",
    "custom_variant3_option",
    # Fulfillment (2)
    "shipping",
    "is_digital",
    # Merchant Info (5)
    "seller_name",
    "marketplace_seller",
    "seller_url",
    "seller_privacy_policy",
    "seller_tos",
    # Returns (4)
    "accepts_returns",
    "return_deadline_in_days",
    "accepts_exchanges",
    "return_policy",
    # Performance Signals (2)
    "popularity_score",
    "return_rate",
    # Compliance (2)
    "warning",
    "age_restriction",
    # Reviews & Q&A (6)
    "review_count",
    "star_rating",
    "store_review_count",
    "store_star_rating",
    "q_and_a",
    "reviews",
    # Related Products (2)
    "related_product_id",
    "relationship_type",
    # Geo Tagging (4)
    "target_countries",
    "store_country",
    "geo_price",
    "geo_availability",
]

# Verifier qu'on a bien 77 colonnes
assert len(all_columns_ordered) == 77, f"Attendu 77 colonnes, obtenu {len(all_columns_ordered)}"

# Supprimer les colonnes temporaires
for tmp_col in ["_shipping_weight", "_rich_desc", "_xlsx_category"]:
    if tmp_col in df.columns:
        df.drop(columns=[tmp_col], inplace=True)

# S'assurer que toutes les colonnes existent dans le DataFrame
for col in all_columns_ordered:
    if col not in df.columns:
        df[col] = ""

df = df[all_columns_ordered]

# --- 11. Exporter ---
output_file = "ACP_OpenAI_Feed.csv"
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"Fichier ACP genere : {output_file}")
print(f"  - {len(df)} produits")
print(f"  - {len(df.columns)} colonnes (spec = 77)")
print(f"  - Produits avec variations : {(df['listing_has_variations'] == 'true').sum()}")
print(f"  - Produits sans variations : {(df['listing_has_variations'] == 'false').sum()}")
print()

# Afficher les colonnes remplies vs vides
filled = []
empty = []
for col in all_columns_ordered:
    non_empty = (df[col] != "").sum()
    if non_empty > 0:
        filled.append(f"  {col}: {non_empty}/{len(df)}")
    else:
        empty.append(f"  {col}")

print(f"Colonnes remplies ({len(filled)}):")
for f in filled:
    print(f)
print(f"\nColonnes vides ({len(empty)}):")
for e in empty:
    print(e)
