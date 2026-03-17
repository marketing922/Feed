"""
Outil de mise a jour automatique des feeds ACP et GMC
Laboratoire Calebasse
"""

import streamlit as st
import pandas as pd
import re
import json
import os
import glob
import io
import hashlib
from datetime import datetime

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "Files")
FILES_UPDATE_DIR = os.path.join(BASE_DIR, "Files to update")
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")
ACP_FEED = os.path.join(FILES_UPDATE_DIR, "ACP_OpenAI_Feed.csv")
ETIQUETTE_AB = os.path.join(FILES_DIR, "Etiquette-AB - final.csv")
ETIQUETTE_CD = os.path.join(FILES_DIR, "Etiquette-CD - final.csv")
RELATED_JSON = os.path.join(SCRIPTS_DIR, "related_products.json")
GMC_PATTERN = os.path.join(FILES_UPDATE_DIR, "Flux Google*")

def find_gmc_file():
    """Trouver le fichier GMC malgre les caracteres speciaux."""
    files = glob.glob(GMC_PATTERN)
    return files[0] if files else None

# --- Helpers ---

def extract_barcodes():
    """Extraire les codes-barres des fichiers Etiquette."""
    barcodes = {}
    for path in [ETIQUETTE_AB, ETIQUETTE_CD]:
        if not os.path.exists(path):
            continue
        et = pd.read_csv(path, dtype=str, keep_default_na=False)
        for _, row in et.iterrows():
            sku = row.get("sku", "").strip()
            url = row.get("codebarre", "").strip()
            if sku and url:
                match = re.search(r"/(\d{13})_", url)
                if match:
                    barcodes[sku] = match.group(1)
    return barcodes


def extract_rich_desc(html):
    if not html or html == "<ul></ul>":
        return ""
    items = re.findall(r"<li>(.*?)</li>", html, re.DOTALL)
    if items:
        cleaned = [re.sub(r"<[^>]+>", "", item).strip() for item in items if re.sub(r"<[^>]+>", "", item).strip()]
        return ", ".join(cleaned).lower()
    # Fallback: strip all HTML tags
    text = re.sub(r"<[^>]+>", "", html).strip()
    return text.lower()


def fix_price(val):
    """Normalise un prix au format  '8,15 EUR'."""
    if not val or val.strip() == "":
        return ""
    v = val.strip()
    # Retirer un eventuel suffixe devise existant (EUR, €, etc.)
    v = re.sub(r"\s*(EUR|€)\s*$", "", v, flags=re.IGNORECASE).strip()
    # Normaliser le separateur decimal : point -> virgule
    v = v.replace(".", ",")
    # S'assurer qu'on a bien un format numerique
    if re.match(r"^\d+,\d+$", v) or re.match(r"^\d+$", v):
        return v + " EUR"
    return v + " EUR"


def get_custom_variant_format(title):
    t = title.lower()
    if "poudre concentr" in t:
        return "Poudre concentree"
    if "gelules" in t or "gélules" in t:
        return "Gelules"
    if "grand sachet" in t:
        return "Grand Sachet"
    if "petit sachet" in t:
        return "Petit Sachet"
    if "sachets" in t or "sachet" in t:
        return "Sachet"
    if "flacon" in t:
        return "Flacon"
    return ""


def get_weight_from_title(title):
    match = re.search(r"(\d+)\s*g\b", title, re.IGNORECASE)
    return match.group(1) + "g" if match else ""


def build_variant_dict(title):
    variant = {}
    t = title.lower()
    if "poudre concentr" in t:
        variant["format"] = "Poudre concentree"
    elif "gelules" in t or "gélules" in t:
        variant["format"] = "Gelules"
    elif "grand sachet" in t:
        variant["format"] = "Grand Sachet"
    elif "petit sachet" in t:
        variant["format"] = "Petit Sachet"
    elif "sachets" in t or "sachet" in t:
        variant["format"] = "Sachet"
    w = re.search(r"(\d+\s*[gG](?:r)?)\b", title)
    if w:
        variant["poids"] = w.group(1).strip()
    return json.dumps(variant, ensure_ascii=False) if variant else ""


def build_group_title(title):
    parts = title.split(" - ")
    if len(parts) >= 2:
        return " - ".join(parts[:2]).strip()
    return title


# Q&A generique
QA_LIST = [
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

WARNING_STANDARD = (
    "Complement alimentaire deconseille aux enfants de moins de 12 ans. "
    "Deconseille aux femmes enceintes et allaitantes. "
    "Ne peut se substituer a une alimentation diversifiee et un mode de vie sain. "
    "Ne pas depasser la dose journaliere recommandee. "
    "Conserver au sec, a l'abri de la lumiere et de l'humidite. "
    "Tenir hors de portee des enfants."
)

ACP_COLUMNS = [
    "is_eligible_search", "is_eligible_checkout",
    "item_id", "gtin", "mpn", "identifier_exists", "title", "description", "url",
    "brand", "condition", "product_category", "material",
    "dimensions", "length", "width", "height", "dimensions_unit",
    "weight", "item_weight_unit", "age_group",
    "image_url", "additional_image_urls", "video_url", "model_3d_url",
    "price", "sale_price", "sale_price_start_date", "sale_price_end_date",
    "unit_pricing_measure", "pricing_trend",
    "availability", "availability_date", "expiration_date", "pickup_method", "pickup_sla",
    "group_id", "listing_has_variations", "variant_dict", "item_group_title",
    "color", "size", "size_system", "gender", "offer_id",
    "custom_variant1_category", "custom_variant1_option",
    "custom_variant2_category", "custom_variant2_option",
    "custom_variant3_category", "custom_variant3_option",
    "shipping", "is_digital",
    "seller_name", "marketplace_seller", "seller_url", "seller_privacy_policy", "seller_tos",
    "accepts_returns", "return_deadline_in_days", "accepts_exchanges", "return_policy",
    "popularity_score", "return_rate",
    "warning", "age_restriction",
    "review_count", "star_rating", "store_review_count", "store_star_rating",
    "q_and_a", "reviews",
    "related_product_id", "relationship_type",
    "target_countries", "store_country", "geo_price", "geo_availability",
]


def generate_acp(xlsx_bytes, log):
    """Generer le feed ACP a partir du GMC XLSX + XLSX ERP importe."""
    # Charger le GMC comme base (remplace l'ancien CSV Integration)
    gmc_path = find_gmc_file()
    if not gmc_path:
        log.append("! Fichier GMC introuvable, impossible de generer l'ACP")
        return pd.DataFrame(), {}
    df = pd.read_excel(gmc_path, dtype=str, keep_default_na=False)
    dx = pd.read_excel(io.BytesIO(xlsx_bytes), dtype=str, keep_default_na=False)
    dx["id"] = dx["id"].str.strip()
    df["id"] = df["id"].str.strip()

    dx_idx = dx.set_index("id")
    stats = {}

        link_cols = ["image link", "additional image link", "link"]
        dx = replace_semicolon_with_comma(dx, link_cols)
        gmc = replace_semicolon_with_comma(gmc, link_cols)
    # a) Nouveaux produits
    new_ids = set(dx["id"]) - set(df["id"])
    if new_ids:
        new_rows = dx[dx["id"].isin(new_ids)].copy()
        # Enrichir descriptions des nouveaux produits avant renommage
        if "rich_text_description" in new_rows.columns:
            for idx in new_rows.index:
                rich = extract_rich_desc(new_rows.at[idx, "rich_text_description"])
                if rich:
                    base = new_rows.at[idx, "description"].strip()
                    if base:
                        new_rows.at[idx, "description"] = base + " Ses principaux bienfaits : " + rich
                    else:
                        new_rows.at[idx, "description"] = "Ses principaux bienfaits : " + rich
        new_rows.rename(columns={
            "url": "link", "image_link": "image link",
            "additional_image_link": "additional image link",
            "item_group_id": "item group id",
        }, inplace=True)
        for col in df.columns:
            if col not in new_rows.columns:
                new_rows[col] = ""
        new_rows["brand"] = "Laboratoire Calebasse"
        new_rows["condition"] = "new"
        new_rows["title"] = new_rows["title"].apply(lambda t: " ".join(t.split()))
        avail_map = {"AVAILABLE": "in_stock", "OUT_OF_STOCK": "out_of_stock", "AVAILABLE_SOON": "out_of_stock"}
        new_rows["availability"] = new_rows["availability"].map(avail_map).fillna("out_of_stock")
        df = pd.concat([df, new_rows[df.columns]], ignore_index=True)
    stats["nouveaux"] = len(new_ids)
    log.append(f"+ {len(new_ids)} nouveaux produits")

    # b) Retirer les absents (garder dans un sheet separe)
    removed_ids = set(df["id"]) - set(dx["id"])
    removed_df = df[df["id"].isin(removed_ids)].copy() if removed_ids else pd.DataFrame()
    if removed_ids:
        df = df[~df["id"].isin(removed_ids)].reset_index(drop=True)
    stats["retires"] = len(removed_ids)
    log.append(f"- {len(removed_ids)} produits retires")

    # c) MAJ champs communs
    common_mask = df["id"].isin(dx_idx.index)
    common_ids = df.loc[common_mask, "id"]

    avail_map = {"AVAILABLE": "in_stock", "OUT_OF_STOCK": "out_of_stock", "AVAILABLE_SOON": "out_of_stock"}
    new_avail = common_ids.map(lambda i: avail_map.get(dx_idx.loc[i, "availability"], "out_of_stock"))
    changed_avail = int((df.loc[common_mask, "availability"] != new_avail).sum())
    df.loc[common_mask, "availability"] = new_avail.values
    stats["disponibilites"] = changed_avail
    log.append(f"~ {changed_avail} disponibilites mises a jour")

    new_titles = common_ids.map(lambda i: " ".join(dx_idx.loc[i, "title"].split()))
    changed_titles = int((df.loc[common_mask, "title"] != new_titles).sum())
    df.loc[common_mask, "title"] = new_titles.values
    stats["titres"] = changed_titles
    log.append(f"~ {changed_titles} titres mis a jour")

    # Description de base (avant enrichissement)
    new_descs = common_ids.map(lambda i: dx_idx.loc[i, "description"].strip() if dx_idx.loc[i, "description"] else "")
    df.loc[common_mask, "description"] = new_descs.where(new_descs != "", df.loc[common_mask, "description"]).values

    new_imgs = common_ids.map(lambda i: dx_idx.loc[i, "image_link"].strip() if dx_idx.loc[i, "image_link"] else "")
    changed_imgs = int(((new_imgs != "") & (df.loc[common_mask, "image link"] != new_imgs)).sum())
    df.loc[common_mask, "image link"] = new_imgs.where(new_imgs != "", df.loc[common_mask, "image link"]).values
    stats["images"] = changed_imgs
    log.append(f"~ {changed_imgs} images mises a jour")

    new_addimgs = common_ids.map(lambda i: dx_idx.loc[i, "additional_image_link"].strip() if dx_idx.loc[i, "additional_image_link"] else "")
    df.loc[common_mask, "additional image link"] = new_addimgs.where(
        new_addimgs != "", df.loc[common_mask, "additional image link"]
    ).values

    new_urls = common_ids.map(lambda i: dx_idx.loc[i, "url"].strip() if dx_idx.loc[i, "url"] else "")
    changed_urls = int(((new_urls != "") & (df.loc[common_mask, "link"] != new_urls)).sum())
    df.loc[common_mask, "link"] = new_urls.where(new_urls != "", df.loc[common_mask, "link"]).values
    stats["urls"] = changed_urls
    log.append(f"~ {changed_urls} URLs mises a jour")

    new_grps = common_ids.map(lambda i: dx_idx.loc[i, "item_group_id"].strip() if dx_idx.loc[i, "item_group_id"] else "")
    df.loc[common_mask, "item group id"] = new_grps.where(new_grps != "", df.loc[common_mask, "item group id"]).values

    # Shipping weight
    df["_shipping_weight"] = ""
    new_weights = common_ids.map(lambda i: dx_idx.loc[i, "shipping_weight"].strip() if dx_idx.loc[i, "shipping_weight"] else "")
    df.loc[common_mask, "_shipping_weight"] = new_weights.values
    if new_ids:
        new_mask = df["id"].isin(new_ids)
        if new_mask.any():
            df.loc[new_mask, "_shipping_weight"] = df.loc[new_mask, "id"].map(
                lambda i: dx_idx.loc[i, "shipping_weight"].strip() if i in dx_idx.index and dx_idx.loc[i, "shipping_weight"] else ""
            ).values

    # Rich text description (compatible 12 ou 13 colonnes)
    df["_rich_desc"] = ""
    if "rich_text_description" in dx_idx.columns:
        rich_descs = common_ids.map(lambda i: extract_rich_desc(dx_idx.loc[i, "rich_text_description"]) if dx_idx.loc[i, "rich_text_description"] else "")
        df.loc[common_mask, "_rich_desc"] = rich_descs.values

    # Category
    df["_xlsx_category"] = ""
    cats = common_ids.map(lambda i: dx_idx.loc[i, "category"].strip() if dx_idx.loc[i, "category"] else "")
    df.loc[common_mask, "_xlsx_category"] = cats.values

    # --- Renommer colonnes ---
    rename_map = {
        "id": "item_id", "link": "url", "image link": "image_url",
        "additional image link": "additional_image_urls",
        "item group id": "group_id", "product_type": "product_category",
        "sale price": "sale_price",
        "sale price effective date": "sale_price_effective_date",
        "availability date": "availability_date",
        "expiration date": "expiration_date",
        "age group": "age_group", "size system": "size_system",
        "unit pricing measure": "unit_pricing_measure",
        "unit pricing base measure": "unit_pricing_base_measure",
    }
    df.rename(columns=rename_map, inplace=True)

    # Enrichir descriptions : description + "Ses principaux bienfaits : " + rich_text
    mask = (df["description"] == "") & (df["_rich_desc"] != "")
    df.loc[mask, "description"] = "Ses principaux bienfaits : " + df.loc[mask, "_rich_desc"]
    mask2 = (df["description"] != "") & (df["_rich_desc"] != "")
    df.loc[mask2, "description"] = df.loc[mask2, "description"] + " Ses principaux bienfaits : " + df.loc[mask2, "_rich_desc"]

    # Category fallback
    if "_xlsx_category" in df.columns and "product_category" in df.columns:
        mask = (df["product_category"] == "") & (df["_xlsx_category"] != "")
        df.loc[mask, "product_category"] = df.loc[mask, "_xlsx_category"]

    # Supprimer colonnes Google-only
    cols_to_drop = [
        "mobile link", "identifier exists", "product highlight",
        "product detail", "pattern", "is bundle",
        "energy efficiency class", "min energy efficiency class",
        "sell on google quantity", "google_product_category",
        "adult", "size type",
    ]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    # Prix
    df["price"] = df["price"].apply(fix_price)
    if "sale_price" in df.columns:
        df["sale_price"] = df["sale_price"].apply(fix_price)

    # ACP required fields
    df["is_eligible_search"] = "true"
    df["is_eligible_checkout"] = "true"
    df["seller_name"] = "Laboratoire Calebasse"
    df["seller_url"] = "https://calebasse.com"
    df["seller_privacy_policy"] = "https://calebasse.com/politique-confidentialite"
    df["seller_tos"] = "https://calebasse.com/cgv"
    df["target_countries"] = "FR,AL,DE,AD,AT,BE,BY,BA,BG,CY,HR,DK,ES,ES,IC,EA,IC,EA,EE,FI,CP,GF,MQ,YT,NC,PF,RE,BL,SM,PM,TF,WF,GR,HK,HU,IE,IS,IT,KZ,XK,LV,LT,LU,MK,MT,MD,MC,ME,NO,NL,PL,PT,CZ,RO,GB,SK,SE,CH,VA"
    df["store_country"] = "FR"

    # MPN : sku-{item_id}
    df["mpn"] = df["item_id"].apply(lambda x: "sku-" + x.strip() if x.strip() else "")

    group_counts = df[df["group_id"] != ""].groupby("group_id")["item_id"].count()
    multi = set(group_counts[group_counts > 1].index)
    df["listing_has_variations"] = df["group_id"].apply(lambda g: "true" if g in multi else "false")
    df["return_policy"] = "https://calebasse.com/cgv"

    # sale_price_effective_date split
    if "sale_price_effective_date" in df.columns:
        def split_date(val, idx):
            if not val or "/" not in val:
                return ""
            parts = val.split("/")
            return parts[idx].strip() if idx < len(parts) else ""
        df["sale_price_start_date"] = df["sale_price_effective_date"].apply(lambda v: split_date(v, 0))
        df["sale_price_end_date"] = df["sale_price_effective_date"].apply(lambda v: split_date(v, 1))
        df.drop(columns=["sale_price_effective_date"], inplace=True)

    # Variants
    df["variant_dict"] = df["title"].apply(build_variant_dict)
    df["item_group_title"] = df["title"].apply(build_group_title)
    df["custom_variant1_category"] = "Format"
    df["custom_variant1_option"] = df["title"].apply(get_custom_variant_format)
    df["custom_variant2_category"] = "Poids"
    df["custom_variant2_option"] = df["title"].apply(get_weight_from_title)
    df["custom_variant3_category"] = ""
    df["custom_variant3_option"] = ""

    # Optional defaults
    df["shipping"] = "FR:::0.00 EUR:2-5 days"
    df["is_digital"] = "false"
    df["accepts_returns"] = "true"
    df["return_deadline_in_days"] = "14"
    df["accepts_exchanges"] = "true"
    df["warning"] = WARNING_STANDARD
    df["age_restriction"] = "12"
    for col in ["video_url", "model_3d_url", "dimensions", "length", "width", "height",
                "dimensions_unit", "pricing_trend", "unit_pricing_measure",
                "unit_pricing_base_measure", "pickup_sla"]:
        if col not in df.columns:
            df[col] = ""
    if "pickup_method" not in df.columns:
        df["pickup_method"] = "in_store"
    df["marketplace_seller"] = ""
    df["offer_id"] = ""
    df["popularity_score"] = ""
    df["return_rate"] = ""
    df["review_count"] = ""
    df["star_rating"] = ""
    df["store_review_count"] = ""
    df["store_star_rating"] = ""
    df["q_and_a"] = json.dumps(QA_LIST, ensure_ascii=False)
    df["reviews"] = ""

    # Weight
    df["weight"] = df["title"].apply(get_weight_from_title)
    no_weight = df["weight"] == ""
    has_w = df["_shipping_weight"] != ""
    df.loc[no_weight & has_w, "weight"] = df.loc[no_weight & has_w, "_shipping_weight"].apply(
        lambda w: str(int(float(w))) + "g" if w else ""
    )
    df["item_weight_unit"] = df["weight"].apply(lambda w: "g" if w else "")
    df["weight"] = df["weight"].apply(lambda w: w.replace("g", "") if w else "")

    # Related products
    if os.path.exists(RELATED_JSON):
        with open(RELATED_JSON, "r", encoding="utf-8") as f:
            related_map = json.load(f)
        df["related_product_id"] = df["group_id"].apply(
            lambda g: ",".join(related_map[g]) if g in related_map else ""
        )
        df["relationship_type"] = df["related_product_id"].apply(
            lambda r: "often_bought_with" if r else ""
        )
    else:
        df["related_product_id"] = ""
        df["relationship_type"] = ""

    df["geo_price"] = ""
    df["geo_availability"] = ""

    # GTIN from barcodes
    barcodes = extract_barcodes()
    if barcodes:
        # item_id dans ACP = ancien id (sku)
        if "gtin" not in df.columns:
            df["gtin"] = ""
        for idx, row in df.iterrows():
            item_id = row["item_id"]
            # Chercher le sku dans les barcodes (item_id commence parfois par le sku)
            if item_id in barcodes and not df.at[idx, "gtin"]:
                df.at[idx, "gtin"] = barcodes[item_id]
            # Aussi chercher via mpn (sku-XXX -> XXX)
            mpn = row.get("mpn", "")
            if mpn:
                sku_from_mpn = mpn.replace("sku-", "") if mpn.startswith("sku-") else mpn
                if sku_from_mpn in barcodes and not df.at[idx, "gtin"]:
                    df.at[idx, "gtin"] = barcodes[sku_from_mpn]
        gtin_count = (df["gtin"] != "").sum()
        stats["gtin"] = int(gtin_count)
        log.append(f"= {gtin_count} codes-barres GTIN remplis")

    # Supprimer colonnes temp
    for tmp in ["_shipping_weight", "_rich_desc", "_xlsx_category"]:
        if tmp in df.columns:
            df.drop(columns=[tmp], inplace=True)

    # identifier_exists en fonction du gtin
    if "gtin" in df.columns:
        df["identifier_exists"] = df["gtin"].apply(lambda g: "true" if g and g.strip() else "false")

    # Ordonner les 77 colonnes
    for col in ACP_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[ACP_COLUMNS]

    stats["total"] = len(df)
    log.append(f"= {len(df)} produits, {len(df.columns)} colonnes")
    return df, stats, removed_df
    def replace_semicolon_with_comma(df, columns):
        """Remplace les points-virgules par des virgules dans les colonnes de liens."""
        for col in columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.replace(';', ',') if isinstance(x, str) else x)
        return df
        # Correction des points-virgules dans les colonnes de liens
        link_cols = ["image_url", "additional_image_urls", "url"]
        df = replace_semicolon_with_comma(df, link_cols)


def generate_gmc(xlsx_bytes, log):
    """Generer le fichier GMC mis a jour."""
    gmc_path = find_gmc_file()
    if not gmc_path:
        log.append("! Fichier GMC introuvable")
        return None, {}

    gmc = pd.read_excel(gmc_path, dtype=str, keep_default_na=False)
    dx = pd.read_excel(io.BytesIO(xlsx_bytes), dtype=str, keep_default_na=False)
    dx["id"] = dx["id"].str.strip()
    gmc["id"] = gmc["id"].str.strip()

    dx_idx = dx.set_index("id")
    stats = {}

    # a) Nouveaux produits
    new_ids = set(dx["id"]) - set(gmc["id"])
    if new_ids:
        new_rows = dx[dx["id"].isin(new_ids)].copy()
        # Enrichir descriptions des nouveaux produits avant renommage
        if "rich_text_description" in new_rows.columns:
            for idx in new_rows.index:
                rich = extract_rich_desc(new_rows.at[idx, "rich_text_description"])
                if rich:
                    base = new_rows.at[idx, "description"].strip()
                    if base:
                        new_rows.at[idx, "description"] = base + " Ses principaux bienfaits : " + rich
                    else:
                        new_rows.at[idx, "description"] = "Ses principaux bienfaits : " + rich
        rename_cols = {
            "url": "link", "image_link": "image link",
            "additional_image_link": "additional image link",
            "item_group_id": "item group id",
            "sale_price": "sale price",
            "shipping_weight": "shipping_weight_tmp",
            "category": "category_tmp",
        }
        if "rich_text_description" in new_rows.columns:
            rename_cols["rich_text_description"] = "rich_text_tmp"
        new_rows.rename(columns=rename_cols, inplace=True)
        for col in gmc.columns:
            if col not in new_rows.columns:
                new_rows[col] = ""
        new_rows["brand"] = "Laboratoire Calebasse"
        new_rows["condition"] = "new"
        new_rows["title"] = new_rows["title"].apply(lambda t: " ".join(t.split()))
        new_rows["identifier exists"] = "no"
        new_rows["adult"] = "no"
        avail_map = {"AVAILABLE": "in_stock", "OUT_OF_STOCK": "out_of_stock", "AVAILABLE_SOON": "out_of_stock"}
        new_rows["availability"] = new_rows["availability"].map(avail_map).fillna("out_of_stock")
        gmc = pd.concat([gmc, new_rows[gmc.columns]], ignore_index=True)
    stats["nouveaux"] = len(new_ids)
    log.append(f"GMC: + {len(new_ids)} nouveaux produits")

    # b) Retirer absents (garder dans un sheet separe)
    removed_ids = set(gmc["id"]) - set(dx["id"])
    gmc_removed_df = gmc[gmc["id"].isin(removed_ids)].copy() if removed_ids else pd.DataFrame()
    if removed_ids:
        gmc = gmc[~gmc["id"].isin(removed_ids)].reset_index(drop=True)
    stats["retires"] = len(removed_ids)
    log.append(f"GMC: - {len(removed_ids)} produits retires")

    # c) MAJ champs communs
    common_mask = gmc["id"].isin(dx_idx.index)
    common_ids = gmc.loc[common_mask, "id"]

    avail_map = {"AVAILABLE": "in_stock", "OUT_OF_STOCK": "out_of_stock", "AVAILABLE_SOON": "out_of_stock"}
    new_avail = common_ids.map(lambda i: avail_map.get(dx_idx.loc[i, "availability"], "out_of_stock"))
    changed_avail = int((gmc.loc[common_mask, "availability"] != new_avail).sum())
    gmc.loc[common_mask, "availability"] = new_avail.values
    stats["disponibilites"] = changed_avail
    log.append(f"GMC: ~ {changed_avail} disponibilites")

    new_titles = common_ids.map(lambda i: " ".join(dx_idx.loc[i, "title"].split()))
    changed_titles = int((gmc.loc[common_mask, "title"] != new_titles).sum())
    gmc.loc[common_mask, "title"] = new_titles.values
    stats["titres"] = changed_titles
    log.append(f"GMC: ~ {changed_titles} titres")

    # Description de base (avant enrichissement)
    new_descs = common_ids.map(lambda i: dx_idx.loc[i, "description"].strip() if dx_idx.loc[i, "description"] else "")
    gmc.loc[common_mask, "description"] = new_descs.where(new_descs != "", gmc.loc[common_mask, "description"]).values

    new_imgs = common_ids.map(lambda i: dx_idx.loc[i, "image_link"].strip() if dx_idx.loc[i, "image_link"] else "")
    gmc.loc[common_mask, "image link"] = new_imgs.where(new_imgs != "", gmc.loc[common_mask, "image link"]).values

    new_addimgs = common_ids.map(lambda i: dx_idx.loc[i, "additional_image_link"].strip() if dx_idx.loc[i, "additional_image_link"] else "")
    gmc.loc[common_mask, "additional image link"] = new_addimgs.where(
        new_addimgs != "", gmc.loc[common_mask, "additional image link"]
    ).values

    new_urls = common_ids.map(lambda i: dx_idx.loc[i, "url"].strip() if dx_idx.loc[i, "url"] else "")
    gmc.loc[common_mask, "link"] = new_urls.where(new_urls != "", gmc.loc[common_mask, "link"]).values

    new_grps = common_ids.map(lambda i: dx_idx.loc[i, "item_group_id"].strip() if dx_idx.loc[i, "item_group_id"] else "")
    gmc.loc[common_mask, "item group id"] = new_grps.where(new_grps != "", gmc.loc[common_mask, "item group id"]).values

    # Prix
    new_prices = common_ids.map(lambda i: dx_idx.loc[i, "price"].strip() if dx_idx.loc[i, "price"] else "")
    gmc.loc[common_mask, "price"] = new_prices.where(new_prices != "", gmc.loc[common_mask, "price"]).values

    # Sale price : ERP fait autorite (ecrase meme si vide pour retirer les promos expirees)
    if "sale_price" in dx_idx.columns and "sale price" in gmc.columns:
        new_sale = common_ids.map(lambda i: dx_idx.loc[i, "sale_price"].strip() if dx_idx.loc[i, "sale_price"] else "")
        gmc.loc[common_mask, "sale price"] = new_sale.values

    # Description enrichie : description + "Ses principaux bienfaits : " + rich_text
    if "description" in gmc.columns and "rich_text_description" in dx_idx.columns:
        rich_descs = common_ids.map(
            lambda i: extract_rich_desc(dx_idx.loc[i, "rich_text_description"])
            if dx_idx.loc[i, "rich_text_description"] else ""
        )
        mask_empty = (gmc.loc[common_mask, "description"] == "") & (rich_descs != "")
        gmc.loc[common_mask & mask_empty.values, "description"] = "Ses principaux bienfaits : " + rich_descs[mask_empty].values
        mask_both = (gmc.loc[common_mask, "description"] != "") & (rich_descs != "") & (~mask_empty)
        if mask_both.any():
            idxs = common_mask & mask_both.values
            gmc.loc[idxs, "description"] = gmc.loc[idxs, "description"] + " Ses principaux bienfaits : " + rich_descs[mask_both].values

    # GTIN from barcodes
    barcodes = extract_barcodes()
    if barcodes and "gtin" in gmc.columns:
        for idx, row in gmc.iterrows():
            item_id = row["id"]
            if item_id in barcodes and not gmc.at[idx, "gtin"]:
                gmc.at[idx, "gtin"] = barcodes[item_id]
            mpn = row.get("mpn", "")
            if mpn:
                sku = mpn.replace("sku-", "") if mpn.startswith("sku-") else mpn
                if sku in barcodes and not gmc.at[idx, "gtin"]:
                    gmc.at[idx, "gtin"] = barcodes[sku]

    # MPN : sku-{id}
    if "mpn" in gmc.columns:
        gmc["mpn"] = gmc["id"].apply(lambda x: "sku-" + x.strip() if x.strip() else "")

    # identifier exists en fonction du gtin
    if "gtin" in gmc.columns and "identifier exists" in gmc.columns:
        gmc["identifier exists"] = gmc["gtin"].apply(lambda g: "yes" if g and g.strip() else "no")

    # Prix : format "X,XX EUR"
    if "price" in gmc.columns:
        gmc["price"] = gmc["price"].apply(fix_price)
    if "sale price" in gmc.columns:
        gmc["sale price"] = gmc["sale price"].apply(fix_price)

    stats["total"] = len(gmc)
    log.append(f"GMC: = {len(gmc)} produits, {len(gmc.columns)} colonnes")
    return gmc, stats, gmc_removed_df


# ============================================================
# HELPERS: Charts & stats for preview
# ============================================================

def html_bar_chart(labels, values, color="#89B832"):
    """Render a bar chart as HTML (avoids altair dependency)."""
    if not values:
        return
    max_val = max(values) if max(values) > 0 else 1
    bars_html = ""
    for label, val in zip(labels, values):
        pct = val / max_val * 100
        bars_html += f"""
        <div style="display:flex;align-items:center;margin:6px 0;font-family:'Manrope',sans-serif;">
            <div style="width:180px;font-size:13px;color:#1A1A1A;text-align:right;padding-right:12px;flex-shrink:0;">{label}</div>
            <div style="flex:1;background:#E5E5E5;border-radius:4px;height:26px;overflow:hidden;">
                <div style="width:{pct}%;background:{color};height:100%;border-radius:4px;min-width:2px;"></div>
            </div>
            <div style="width:60px;font-size:13px;font-weight:600;color:#1A1A1A;padding-left:10px;">{val}</div>
        </div>"""
    st.markdown(bars_html, unsafe_allow_html=True)


def html_histogram(prices_series, bins=15, color="#89B832"):
    """Render a price histogram as HTML."""
    if prices_series.empty:
        return
    cuts = pd.cut(prices_series, bins=bins)
    hist = cuts.value_counts().sort_index()
    labels = [f"{iv.left:.0f}-{iv.right:.0f}" for iv in hist.index]
    values = hist.values.tolist()
    html_bar_chart(labels, values, color)

def column_fill_stats(df):
    """Compute fill rate per column."""
    rows = []
    for col in df.columns:
        non_empty = (df[col] != "").sum()
        rows.append({
            "Colonne": col,
            "Remplis": f"{non_empty}/{len(df)}",
            "Taux": f"{non_empty/len(df)*100:.0f}%",
            "Vide": "Non" if non_empty > 0 else "Oui",
        })
    return pd.DataFrame(rows)


def availability_stats(df, col="availability"):
    """Count availability values."""
    if col not in df.columns:
        return pd.DataFrame()
    counts = df[col].value_counts().reset_index()
    counts.columns = ["Statut", "Nombre"]
    return counts


def price_stats(df, col="price"):
    """Basic price distribution."""
    if col not in df.columns:
        return {}
    raw = df[col].str.replace(r"\s*EUR\s*$", "", regex=True).str.replace(",", ".").str.replace(r"[^\d.]", "", regex=True)
    prices = pd.to_numeric(raw, errors="coerce").dropna()
    if prices.empty:
        return {}
    return {
        "Nb produits avec prix": int(prices.count()),
        "Prix min": f"{prices.min():.2f}",
        "Prix max": f"{prices.max():.2f}",
        "Prix moyen": f"{prices.mean():.2f}",
        "Prix median": f"{prices.median():.2f}",
    }


# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="Calebasse - Mise a jour des feeds",
    page_icon="🌿",
    layout="wide",
)

# ============================================================
# AUTHENTIFICATION
# ============================================================
USERS = {
    "admin": hashlib.sha256("Calebasse2026!".encode()).hexdigest(),
    "calebasse": hashlib.sha256("feeds@Lab".encode()).hexdigest(),
}

def check_login():
    if st.session_state.get("authenticated"):
        return True
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center;margin-top:60px;margin-bottom:30px;">
            <h1 style="font-family:Georgia,serif;color:#89B832;font-size:36px;margin:0;">Laboratoire Calebasse</h1>
            <p style="color:#666;font-style:italic;font-size:14px;margin:6px 0 0;">Gestion des feeds produits</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown('<p style="font-size:15px;font-weight:600;color:#1A1A1A;margin-bottom:4px;">Connexion</p>', unsafe_allow_html=True)
            username = st.text_input("Identifiant")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter", type="primary", use_container_width=True)
            if submitted:
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                if username in USERS and USERS[username] == pwd_hash:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect")
        st.markdown('<div style="text-align:center;margin-top:40px;font-size:12px;color:#bbb;">Laboratoire Calebasse &copy; 2026</div>', unsafe_allow_html=True)
    return False

if not check_login():
    st.stop()

# --- Calebasse Design System (CSS complement au theme config.toml) ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    /* Force light theme (override browser localStorage preference) */
    :root, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    [data-testid="stSidebar"], .main, .block-container,
    [data-testid="stAppViewBlockContainer"] {
        background-color: #F9F9F7 !important;
        color: #1A1A1A !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    .main .stMarkdown, .main p, .main span, .main label, .main li,
    .main h1, .main h2, .main h3, .main h4 {
        color: #1A1A1A !important;
    }
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-color: #E5E5E5 !important;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] p {
        color: #1A1A1A !important;
    }
    .stDataFrame, [data-testid="stTable"] {
        background-color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border-color: #E5E5E5 !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p {
        color: #1A1A1A !important;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #1A1A1A !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background-color: #89B832 !important;
        border-color: #89B832 !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background-color: #7aa52b !important;
        border-color: #7aa52b !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        border-color: #89B832 !important;
        color: #89B832 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #f3fbe8 !important;
    }

    /* Header */
    .calebasse-header {
        border-bottom: 3px solid #89B832;
        padding-bottom: 16px;
        margin-bottom: 28px;
    }
    .calebasse-header h1 {
        font-family: Georgia, serif;
        color: #89B832;
        margin: 0;
        font-size: 34px;
    }
    .calebasse-header p {
        margin: 4px 0 0;
        color: #666;
        font-style: italic;
        font-size: 15px;
    }

    /* Section titles */
    .section-title {
        font-family: Georgia, serif;
        border-bottom: 1px solid #ddd;
        padding-bottom: 8px;
        color: #1A1A1A;
        font-size: 22px;
        margin-top: 28px;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #89B832 !important;
        font-weight: 700 !important;
    }

    /* Success box */
    .success-box {
        background: #f3fbe8;
        border: 1px solid #89B832;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 16px 0;
        font-weight: 600;
        color: #3d5a0f;
    }

    /* Active tab */
    .stTabs [aria-selected="true"] {
        color: #89B832 !important;
        border-bottom-color: #89B832 !important;
    }

    /* Footer */
    .calebasse-footer {
        margin-top: 50px;
        text-align: center;
        font-size: 13px;
        color: #999;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 20px;">
        <h2 style="font-family: Georgia, serif; color: #89B832; margin: 0;">Calebasse</h2>
        <p style="color: #666; font-size: 13px; margin: 4px 0 0;">Gestion des feeds produits</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Importer le fichier Export ERP", "Apercu des fichiers actuels"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    # Sidebar file status summary
    acp_exists = os.path.exists(ACP_FEED)
    gmc_exists = find_gmc_file() is not None
    st.markdown("**Fichiers detectes**")
    st.markdown(f"{'&#9989;' if acp_exists else '&#10060;'} ACP Feed", unsafe_allow_html=True)
    st.markdown(f"{'&#9989;' if gmc_exists else '&#10060;'} GMC Feed", unsafe_allow_html=True)
    st.markdown("---")
    st.caption(f"Connecte : **{st.session_state.get('username', '')}**")
    if st.button("Deconnexion", key="logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()

# --- Header ---
st.markdown("""
<div class="calebasse-header">
    <h1>Laboratoire Calebasse</h1>
    <p>Mise a jour automatique des feeds ACP OpenAI & Google Merchant Center</p>
</div>
""", unsafe_allow_html=True)

# Verifier fichiers statiques
if not find_gmc_file():
    st.error("Fichier manquant : Flux Google Merchant Center XLSX")
    st.stop()

# ============================================================
# PAGE 1 : Importer le fichier Export ERP
# ============================================================
if page == "Importer le fichier Export ERP":

    st.markdown('<h2 class="section-title">Importer le fichier Export ERP</h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Glissez ou selectionnez un fichier export-variants (.xlsx)",
        type=["xlsx"],
        help="Fichier exporte depuis l'ERP (ex: export-variants-2026-03-12.xlsx)",
    )

    if uploaded:
        xlsx_bytes = uploaded.read()

        # Preview
        preview = pd.read_excel(io.BytesIO(xlsx_bytes), dtype=str, nrows=5)
        with st.expander(f"Apercu du fichier importe ({len(pd.read_excel(io.BytesIO(xlsx_bytes), dtype=str))} lignes, {len(preview.columns)} colonnes)", expanded=False):
            st.dataframe(preview, width="stretch")

        st.markdown("---")

        # Generate button
        if st.button("Mettre a jour les feeds", type="primary", width="stretch"):
            acp_log = []
            gmc_log = []

            with st.spinner("Generation du feed ACP OpenAI..."):
                acp_df, acp_stats, acp_removed = generate_acp(xlsx_bytes, acp_log)

            with st.spinner("Generation du feed Google Merchant Center..."):
                gmc_df, gmc_stats, gmc_removed = generate_gmc(xlsx_bytes, gmc_log)

            # Sauvegarder automatiquement en local
            acp_path = os.path.join(BASE_DIR, "ACP_OpenAI_Feed.csv")
            acp_df.to_csv(acp_path, index=False, encoding="utf-8")
            acp_log.append(f"Sauvegarde : {acp_path}")

            gmc_files = glob.glob(GMC_PATTERN)
            if gmc_files and gmc_df is not None:
                with pd.ExcelWriter(gmc_files[0], engine="openpyxl") as writer:
                    gmc_df.to_excel(writer, sheet_name="Products", index=False)
                    if not gmc_removed.empty:
                        gmc_removed.to_excel(writer, sheet_name="Retires", index=False)
                gmc_log.append(f"Sauvegarde : {gmc_files[0]}")
                if not gmc_removed.empty:
                    gmc_log.append(f"  + {len(gmc_removed)} produits retires dans l'onglet 'Retires'")

            # Store in session state for persistence
            st.session_state["acp_df"] = acp_df
            st.session_state["gmc_df"] = gmc_df
            st.session_state["acp_stats"] = acp_stats
            st.session_state["gmc_stats"] = gmc_stats
            st.session_state["acp_log"] = acp_log
            st.session_state["gmc_log"] = gmc_log
            st.session_state["acp_removed"] = acp_removed
            st.session_state["gmc_removed"] = gmc_removed
            st.session_state["generated"] = True

        # --- Display results if generated ---
        if st.session_state.get("generated"):
            acp_df = st.session_state["acp_df"]
            gmc_df = st.session_state["gmc_df"]
            acp_stats = st.session_state["acp_stats"]
            gmc_stats = st.session_state["gmc_stats"]
            acp_log = st.session_state["acp_log"]
            gmc_log = st.session_state["gmc_log"]
            acp_removed = st.session_state.get("acp_removed", pd.DataFrame())
            gmc_removed = st.session_state.get("gmc_removed", pd.DataFrame())

            st.markdown('<div class="success-box">Mise a jour terminee — fichiers sauvegardes automatiquement</div>', unsafe_allow_html=True)

            # --- Stats ---
            st.markdown('<h2 class="section-title">Resultats</h2>', unsafe_allow_html=True)
            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.markdown("""<div style="background:#fff;border:1px solid #E5E5E5;border-left:4px solid #89B832;border-radius:8px;padding:18px 16px 10px;">
                <h3 style="margin:0 0 12px;font-size:16px;color:#89B832;font-family:Georgia,serif;">Feed ACP OpenAI</h3>
                </div>""", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total produits", acp_stats.get("total", 0))
                c2.metric("Nouveaux", f"+{acp_stats.get('nouveaux', 0)}")
                c3.metric("Retires", f"-{acp_stats.get('retires', 0)}")
                c4.metric("GTIN remplis", acp_stats.get("gtin", 0))

                c5, c6, c7, c8 = st.columns(4)
                c5.metric("Disponibilites", f"~{acp_stats.get('disponibilites', 0)}")
                c6.metric("Titres", f"~{acp_stats.get('titres', 0)}")
                c7.metric("Images", f"~{acp_stats.get('images', 0)}")
                c8.metric("URLs", f"~{acp_stats.get('urls', 0)}")

            with col2:
                st.markdown("""<div style="background:#fff;border:1px solid #E5E5E5;border-left:4px solid #1A1A1A;border-radius:8px;padding:18px 16px 10px;">
                <h3 style="margin:0 0 12px;font-size:16px;color:#1A1A1A;font-family:Georgia,serif;">Feed Google Merchant Center</h3>
                </div>""", unsafe_allow_html=True)
                if gmc_df is not None:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total produits", gmc_stats.get("total", 0))
                    c2.metric("Nouveaux", f"+{gmc_stats.get('nouveaux', 0)}")
                    c3.metric("Retires", f"-{gmc_stats.get('retires', 0)}")

                    c4, c5 = st.columns(2)
                    c4.metric("Disponibilites", f"~{gmc_stats.get('disponibilites', 0)}")
                    c5.metric("Titres", f"~{gmc_stats.get('titres', 0)}")

            # Logs
            with st.expander("Journal des operations", expanded=False):
                st.markdown("**ACP:**")
                for line in acp_log:
                    st.text(line)
                st.markdown("**GMC:**")
                for line in gmc_log:
                    st.text(line)

            st.markdown("---")

            # ============================
            # APERCU DES DONNEES GENEREES
            # ============================
            st.markdown('<h2 class="section-title">Apercu des donnees generees</h2>', unsafe_allow_html=True)

            tab_names = ["ACP OpenAI Feed", "Google Merchant Center"]
            if not gmc_removed.empty:
                tab_names.append(f"Produits retires ({len(gmc_removed)})")
            tabs = st.tabs(tab_names)
            tab_acp = tabs[0]
            tab_gmc = tabs[1]

            # --- ACP Preview Tab ---
            with tab_acp:
                st.markdown(f"**{len(acp_df)} produits, {len(acp_df.columns)} colonnes**")

                acp_sub1, acp_sub2, acp_sub3, acp_sub4 = st.tabs([
                    "Tableau", "Colonnes & Remplissage", "Disponibilite", "Prix"
                ])

                with acp_sub1:
                    default_cols = ["item_id", "title", "price", "availability", "gtin", "brand", "image_url"]
                    available_cols = [c for c in default_cols if c in acp_df.columns]
                    selected_cols = st.multiselect(
                        "Colonnes a afficher",
                        options=list(acp_df.columns),
                        default=available_cols,
                        key="acp_cols",
                    )
                    if selected_cols:
                        search = st.text_input("Rechercher un produit (ID ou titre)", key="acp_search")
                        display_df = acp_df[selected_cols]
                        if search:
                            mask = display_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                            display_df = display_df[mask]
                        st.dataframe(display_df, width="stretch", height=450)
                        st.caption(f"{len(display_df)} lignes affichees")

                with acp_sub2:
                    fill_df = column_fill_stats(acp_df)
                    filled_count = (fill_df["Vide"] == "Non").sum()
                    empty_count = (fill_df["Vide"] == "Oui").sum()
                    m1, m2 = st.columns(2)
                    m1.metric("Colonnes remplies", f"{filled_count}/77")
                    m2.metric("Colonnes vides", f"{empty_count}/77")
                    st.dataframe(fill_df, width="stretch", height=450)

                with acp_sub3:
                    avail = availability_stats(acp_df)
                    if not avail.empty:
                        html_bar_chart(avail["Statut"].tolist(), avail["Nombre"].tolist())
                        st.dataframe(avail, width="stretch")

                with acp_sub4:
                    pstats = price_stats(acp_df, "price")
                    if pstats:
                        cols = st.columns(len(pstats))
                        for i, (k, v) in enumerate(pstats.items()):
                            cols[i].metric(k, v)
                        prices = pd.to_numeric(acp_df["price"].str.replace(r"\s*EUR\s*$", "", regex=True).str.replace(",", ".").str.replace(r"[^\d.]", "", regex=True), errors="coerce").dropna()
                        html_histogram(prices)

            # --- GMC Preview Tab ---
            with tab_gmc:
                if gmc_df is not None:
                    st.markdown(f"**{len(gmc_df)} produits, {len(gmc_df.columns)} colonnes**")

                    gmc_sub1, gmc_sub2, gmc_sub3, gmc_sub4 = st.tabs([
                        "Tableau", "Colonnes & Remplissage", "Disponibilite", "Prix"
                    ])

                    with gmc_sub1:
                        gmc_default = ["id", "title", "price", "availability", "gtin", "brand", "image link"]
                        gmc_avail = [c for c in gmc_default if c in gmc_df.columns]
                        gmc_selected = st.multiselect(
                            "Colonnes a afficher",
                            options=list(gmc_df.columns),
                            default=gmc_avail,
                            key="gmc_cols",
                        )
                        if gmc_selected:
                            search_gmc = st.text_input("Rechercher un produit (ID ou titre)", key="gmc_search")
                            display_gmc = gmc_df[gmc_selected]
                            if search_gmc:
                                mask = display_gmc.apply(lambda row: row.astype(str).str.contains(search_gmc, case=False).any(), axis=1)
                                display_gmc = display_gmc[mask]
                            st.dataframe(display_gmc, width="stretch", height=450)
                            st.caption(f"{len(display_gmc)} lignes affichees")

                    with gmc_sub2:
                        gmc_fill = column_fill_stats(gmc_df)
                        filled_g = (gmc_fill["Vide"] == "Non").sum()
                        empty_g = (gmc_fill["Vide"] == "Oui").sum()
                        m1, m2 = st.columns(2)
                        m1.metric("Colonnes remplies", f"{filled_g}/{len(gmc_df.columns)}")
                        m2.metric("Colonnes vides", f"{empty_g}/{len(gmc_df.columns)}")
                        st.dataframe(gmc_fill, width="stretch", height=450)

                    with gmc_sub3:
                        gavail = availability_stats(gmc_df)
                        if not gavail.empty:
                            html_bar_chart(gavail["Statut"].tolist(), gavail["Nombre"].tolist())
                            st.dataframe(gavail, width="stretch")

                    with gmc_sub4:
                        gpstats = price_stats(gmc_df, "price")
                        if gpstats:
                            cols = st.columns(len(gpstats))
                            for i, (k, v) in enumerate(gpstats.items()):
                                cols[i].metric(k, v)
                            prices_g = pd.to_numeric(gmc_df["price"].str.replace(r"\s*EUR\s*$", "", regex=True).str.replace(",", ".").str.replace(r"[^\d.]", "", regex=True), errors="coerce").dropna()
                            html_histogram(prices_g)
                else:
                    st.warning("Fichier GMC non genere")

            # --- Tab Retires ---
            if not gmc_removed.empty and len(tabs) > 2:
                with tabs[2]:
                    st.markdown(f"**{len(gmc_removed)} produits retires** (presents dans GMC/ACP mais absents de l'export ERP)")
                    default_ret = ["id", "title", "price", "availability", "gtin", "brand"]
                    avail_ret = [c for c in default_ret if c in gmc_removed.columns]
                    st.dataframe(gmc_removed[avail_ret] if avail_ret else gmc_removed, width="stretch", height=450)

            st.markdown("---")

            # ============================
            # DOWNLOADS
            # ============================
            st.markdown('<h2 class="section-title">Telecharger</h2>', unsafe_allow_html=True)
            dl1, dl2 = st.columns(2)

            with dl1:
                acp_csv = acp_df.to_csv(index=False, encoding="utf-8")
                st.download_button(
                    label="ACP_OpenAI_Feed.csv",
                    data=acp_csv,
                    file_name="ACP_OpenAI_Feed.csv",
                    mime="text/csv",
                    width="stretch",
                )

            with dl2:
                if gmc_df is not None:
                    gmc_buffer = io.BytesIO()
                    with pd.ExcelWriter(gmc_buffer, engine="openpyxl") as writer:
                        gmc_df.to_excel(writer, sheet_name="Products", index=False)
                        if not gmc_removed.empty:
                            gmc_removed.to_excel(writer, sheet_name="Retires", index=False)
                    gmc_buffer.seek(0)
                    st.download_button(
                        label="Flux Google Merchant Center.xlsx",
                        data=gmc_buffer,
                        file_name="Flux Google Merchant Center - Products source.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch",
                    )


    else:
        st.info("Importez un fichier export-variants (.xlsx) pour commencer")

# ============================================================
# PAGE 2 : Apercu des fichiers actuels
# ============================================================
elif page == "Apercu des fichiers actuels":

    st.markdown('<h2 class="section-title">Etat actuel des fichiers</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        acp_path = os.path.join(BASE_DIR, "ACP_OpenAI_Feed.csv")
        if os.path.exists(acp_path):
            acp_full = pd.read_csv(acp_path, dtype=str, keep_default_na=False)
            st.metric("ACP Feed", f"{len(acp_full)} produits, {len(acp_full.columns)} colonnes")
        else:
            st.warning("ACP_OpenAI_Feed.csv introuvable")
    with col2:
        gmc_path = find_gmc_file()
        if gmc_path:
            gmc = pd.read_excel(gmc_path, dtype=str)
            st.metric("GMC Feed", f"{len(gmc)} produits, {len(gmc.columns)} colonnes")
        else:
            st.warning("GMC XLSX introuvable")

    # Download buttons
    dl1, dl2 = st.columns(2)
    with dl1:
        if os.path.exists(acp_path):
            acp_data = acp_full.to_csv(index=False, encoding="utf-8")
            st.download_button(
                label="Telecharger ACP_OpenAI_Feed.csv",
                data=acp_data,
                file_name="ACP_OpenAI_Feed.csv",
                mime="text/csv",
                key="dl_acp_apercu",
            )
    with dl2:
        if gmc_path:
            gmc_buf = io.BytesIO()
            with pd.ExcelWriter(gmc_buf, engine="openpyxl") as writer:
                gmc.to_excel(writer, sheet_name="Products", index=False)
            st.download_button(
                label="Telecharger GMC.xlsx",
                data=gmc_buf.getvalue(),
                file_name=os.path.basename(gmc_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_gmc_apercu",
            )

    st.markdown("---")

    cur_tab1, cur_tab2 = st.tabs(["ACP OpenAI Feed", "Google Merchant Center"])

    # ==================== ACP TAB ====================
    with cur_tab1:
        acp_path = os.path.join(BASE_DIR, "ACP_OpenAI_Feed.csv")
        if os.path.exists(acp_path):
            cur_acp = pd.read_csv(acp_path, dtype=str, keep_default_na=False)
            st.markdown(f"**{len(cur_acp)} produits, {len(cur_acp.columns)} colonnes**")

            acp_mode = st.radio("Mode", ["Consulter", "Modifier"], horizontal=True, key="acp_mode")

            if acp_mode == "Consulter":
                c_sub1, c_sub2, c_sub3, c_sub4 = st.tabs([
                    "Tableau", "Colonnes & Remplissage", "Disponibilite", "Prix"
                ])

                with c_sub1:
                    cur_default = ["item_id", "title", "price", "availability", "gtin", "brand", "image_url"]
                    cur_avail = [c for c in cur_default if c in cur_acp.columns]
                    cur_sel = st.multiselect(
                        "Colonnes a afficher", list(cur_acp.columns), default=cur_avail, key="cur_acp_cols"
                    )
                    if cur_sel:
                        cur_search = st.text_input("Rechercher", key="cur_acp_search")
                        d = cur_acp[cur_sel]
                        if cur_search:
                            d = d[d.apply(lambda r: r.astype(str).str.contains(cur_search, case=False).any(), axis=1)]
                        st.dataframe(d, width="stretch", height=450)
                        st.caption(f"{len(d)} lignes")

                with c_sub2:
                    fill_cur = column_fill_stats(cur_acp)
                    filled_c = (fill_cur["Vide"] == "Non").sum()
                    empty_c = (fill_cur["Vide"] == "Oui").sum()
                    m1, m2 = st.columns(2)
                    m1.metric("Colonnes remplies", f"{filled_c}/{len(cur_acp.columns)}")
                    m2.metric("Colonnes vides", f"{empty_c}/{len(cur_acp.columns)}")
                    st.dataframe(fill_cur, width="stretch", height=450)

                with c_sub3:
                    avail_c = availability_stats(cur_acp)
                    if not avail_c.empty:
                        html_bar_chart(avail_c["Statut"].tolist(), avail_c["Nombre"].tolist())
                        st.dataframe(avail_c, width="stretch")

                with c_sub4:
                    ps = price_stats(cur_acp, "price")
                    if ps:
                        cols = st.columns(len(ps))
                        for i, (k, v) in enumerate(ps.items()):
                            cols[i].metric(k, v)
                        prices_cur = pd.to_numeric(cur_acp["price"].str.replace(r"\s*EUR\s*$", "", regex=True).str.replace(",", ".").str.replace(r"[^\d.]", "", regex=True), errors="coerce").dropna()
                        html_histogram(prices_cur)

            else:  # Modifier
                st.markdown("""<div style="background:#fff8e1;border:1px solid #f9a825;border-radius:6px;padding:10px 14px;margin-bottom:12px;font-size:13px;color:#6d4c00;">
                Modifiez les cellules directement dans le tableau. Cliquez sur <b>Sauvegarder</b> pour enregistrer.
                </div>""", unsafe_allow_html=True)

                edit_search = st.text_input("Filtrer par SKU ou titre", key="acp_edit_search")
                edit_cols = st.multiselect(
                    "Colonnes a modifier",
                    list(cur_acp.columns),
                    default=["item_id", "title", "description", "price", "sale_price", "availability", "gtin", "image_url"],
                    key="acp_edit_cols",
                )
                if edit_cols:
                    edit_df = cur_acp[edit_cols].copy()
                    if edit_search:
                        mask = edit_df.apply(lambda r: r.astype(str).str.contains(edit_search, case=False).any(), axis=1)
                        edit_idx = edit_df[mask].index
                        edit_df = edit_df.loc[edit_idx]
                    else:
                        edit_idx = edit_df.index

                    edited = st.data_editor(
                        edit_df,
                        use_container_width=True,
                        height=500,
                        num_rows="fixed",
                        key="acp_editor",
                    )

                    b1, b2 = st.columns([1, 4])
                    with b1:
                        if st.button("Sauvegarder ACP", type="primary", key="save_acp"):
                            for col in edit_cols:
                                cur_acp.loc[edit_idx, col] = edited[col].values
                            cur_acp.to_csv(acp_path, index=False, encoding="utf-8")
                            st.success(f"ACP sauvegarde ({len(cur_acp)} produits)")
                            st.rerun()
                    with b2:
                        st.caption(f"{len(edit_df)} lignes affichees / {len(cur_acp)} total")
        else:
            st.info("Aucun fichier ACP trouve")

    # ==================== GMC TAB ====================
    with cur_tab2:
        gmc_path = find_gmc_file()
        if gmc_path:
            cur_gmc = pd.read_excel(gmc_path, dtype=str, keep_default_na=False)
            st.markdown(f"**{len(cur_gmc)} produits, {len(cur_gmc.columns)} colonnes**")

            gmc_mode = st.radio("Mode", ["Consulter", "Modifier"], horizontal=True, key="gmc_mode")

            if gmc_mode == "Consulter":
                g_sub1, g_sub2, g_sub3, g_sub4 = st.tabs([
                    "Tableau", "Colonnes & Remplissage", "Disponibilite", "Prix"
                ])

                with g_sub1:
                    gmc_def = ["id", "title", "price", "availability", "gtin", "brand", "image link"]
                    gmc_av = [c for c in gmc_def if c in cur_gmc.columns]
                    gmc_sel = st.multiselect(
                        "Colonnes a afficher", list(cur_gmc.columns), default=gmc_av, key="cur_gmc_cols"
                    )
                    if gmc_sel:
                        g_search = st.text_input("Rechercher", key="cur_gmc_search")
                        dg = cur_gmc[gmc_sel]
                        if g_search:
                            dg = dg[dg.apply(lambda r: r.astype(str).str.contains(g_search, case=False).any(), axis=1)]
                        st.dataframe(dg, width="stretch", height=450)
                        st.caption(f"{len(dg)} lignes")

                with g_sub2:
                    gmc_fill = column_fill_stats(cur_gmc)
                    filled_g = (gmc_fill["Vide"] == "Non").sum()
                    empty_g = (gmc_fill["Vide"] == "Oui").sum()
                    m1, m2 = st.columns(2)
                    m1.metric("Colonnes remplies", f"{filled_g}/{len(cur_gmc.columns)}")
                    m2.metric("Colonnes vides", f"{empty_g}/{len(cur_gmc.columns)}")
                    st.dataframe(gmc_fill, width="stretch", height=450)

                with g_sub3:
                    gavail_c = availability_stats(cur_gmc)
                    if not gavail_c.empty:
                        html_bar_chart(gavail_c["Statut"].tolist(), gavail_c["Nombre"].tolist())
                        st.dataframe(gavail_c, width="stretch")

                with g_sub4:
                    gps = price_stats(cur_gmc, "price")
                    if gps:
                        cols = st.columns(len(gps))
                        for i, (k, v) in enumerate(gps.items()):
                            cols[i].metric(k, v)
                        prices_gmc_cur = pd.to_numeric(cur_gmc["price"].str.replace(r"\s*EUR\s*$", "", regex=True).str.replace(",", ".").str.replace(r"[^\d.]", "", regex=True), errors="coerce").dropna()
                        html_histogram(prices_gmc_cur)

            else:  # Modifier
                st.markdown("""<div style="background:#fff8e1;border:1px solid #f9a825;border-radius:6px;padding:10px 14px;margin-bottom:12px;font-size:13px;color:#6d4c00;">
                Modifiez les cellules directement dans le tableau. Cliquez sur <b>Sauvegarder</b> pour enregistrer.
                </div>""", unsafe_allow_html=True)

                gedit_search = st.text_input("Filtrer par SKU ou titre", key="gmc_edit_search")
                gedit_cols = st.multiselect(
                    "Colonnes a modifier",
                    list(cur_gmc.columns),
                    default=["id", "title", "description", "price", "sale price", "availability", "gtin", "image link"],
                    key="gmc_edit_cols",
                )
                if gedit_cols:
                    gedit_df = cur_gmc[gedit_cols].copy()
                    if gedit_search:
                        gmask = gedit_df.apply(lambda r: r.astype(str).str.contains(gedit_search, case=False).any(), axis=1)
                        gedit_idx = gedit_df[gmask].index
                        gedit_df = gedit_df.loc[gedit_idx]
                    else:
                        gedit_idx = gedit_df.index

                    gedited = st.data_editor(
                        gedit_df,
                        use_container_width=True,
                        height=500,
                        num_rows="fixed",
                        key="gmc_editor",
                    )

                    gb1, gb2 = st.columns([1, 4])
                    with gb1:
                        if st.button("Sauvegarder GMC", type="primary", key="save_gmc"):
                            for col in gedit_cols:
                                cur_gmc.loc[gedit_idx, col] = gedited[col].values
                            with pd.ExcelWriter(gmc_path, engine="openpyxl") as writer:
                                cur_gmc.to_excel(writer, sheet_name="Products", index=False)
                            st.success(f"GMC sauvegarde ({len(cur_gmc)} produits)")
                            st.rerun()
                    with gb2:
                        st.caption(f"{len(gedit_df)} lignes affichees / {len(cur_gmc)} total")
        else:
            st.info("Aucun fichier GMC trouve")

# Footer
st.markdown('<div class="calebasse-footer">Laboratoire Calebasse &copy; 2026</div>', unsafe_allow_html=True)
