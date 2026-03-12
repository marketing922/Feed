# Comparaison approfondie : fichier ERP vs Flux Google Merchant Center

> **export-variants-2026-03-12.xlsx**  vs **Flux Google Merchant Center** 

---

## Resume global

| Metrique | ERP | Flux google | Ecart |
|----------|:--------------:|:------------:|:-----:|
| Nombre de lignes | 1886 | 1824 | +62 |
| Nombre de colonnes | 13 | 38 | -25 |
| IDs uniques | 1886 | 1824 | +62 |
| IDs en commun | 1792 | 1792 | - |
| IDs seulement dans ERP | **94** | - | Nouveaux produits |
| IDs seulement dans Flux google| - | **32** | Produits supprimes/retires |

---

## 1. Colonnes

### Correspondance des colonnes

| ERP | Flux google | Match |
|------|-----|:-----:|
| `id` | `id` | Direct |
| `title` | `title` | Direct |
| `description` | `description` | Direct |
| `url` | `link` | Renomme |
| `price` | `price` | Direct |
| `sale_price` | `sale price` | Direct |
| `availability` | `availability` | Direct (format different) |
| `image_link` | `image link` | Renomme |
| `additional_image_link` | `additional image link` | Renomme |
| `shipping_weight` | _(absent)_ |  |
| `item_group_id` | `item group id` | Renomme |
| `rich_text_description` | _(absent)_ |  |
| `category` | _(absent)_ | |

### 3 colonnes presentes dans le fichier ERP mais absentes du Flux google

| Colonne | Remplissage | Utilite |
|---------|:-----------:|---------|
| `shipping_weight` | 1657/1886 (88%) | Poids en grammes - utile pour le champ `weight` ACP |
| `rich_text_description` | 1399/1886 (74%) | Description HTML avec bullet points - enrichit la description |
| `category` | 1767/1886 (94%) | Categories du site (ex: "Bio, Digestion") |

### 25 colonnes presentes dans CSV mais absentes du XLSX

`availability date`, `expiration date`, `mobile link`, `sale price effective date`, `identifier exists`, `gtin`, `mpn`, `brand`, `product highlight`, `product detail`, `condition`, `adult`, `color`, `size`, `size type`, `size system`, `gender`, `material`, `pattern`, `age group`, `is bundle`, `unit pricing measure`, `unit pricing base measure`, `energy efficiency class`, `min energy efficiency class`, `product_type`, `sell on google quantity`, `google_product_category`

> La plupart sont des champs Google Shopping quasi vides dans le CSV.

---

## 2. Produits (IDs)

### 94 produits presents UNIQUEMENT dans le XLSX (nouveaux)

| Statut | Nombre |
|--------|:------:|
| AVAILABLE | 72 |
| OUT_OF_STOCK | 17 |
| AVAILABLE_SOON | 5 |

**Categories des nouveaux produits :**

| Categorie | Nombre |
|-----------|:------:|
| Materiel MTC (moxa, aiguilles couteau...) | ~45 |
| Packs & coffrets cadeaux | ~12 |
| Bio (plantes bio) | ~8 |
| Gruaux | ~6 |
| Formules & complements | ~15 |
| Divers (bougie, mannequin...) | ~8 |

<details>
<summary>Liste complete des 94 nouveaux produits</summary>

| ID | Titre | Prix | Statut |
|----|-------|:----:|:------:|
| AQSMYZX2 | Gruau aux Jujubes et Lys x2 | 19.00 | AVAILABLE |
| AYYRCP | Astragale + Yi yi ren poudre concentree | 37.90 | AVAILABLE |
| AYYRPCP | Astragale + Yi yi ren poudre concentree (promo) | 37.90 | AVAILABLE |
| CBCJGL | Ba zhen wan gelules | 37.90 | AVAILABLE |
| CBCJGLCP | Ba zhen wan poudre concentree | 37.90 | AVAILABLE |
| CBYSPGL | Bu yi shen pin gelules | 37.90 | AVAILABLE |
| CBYSPGLCP | Bu yi shen pin poudre concentree | 37.90 | AVAILABLE |
| COF-ESG | Coffret Epure Detox SuperGreen | 62.80 | AVAILABLE |
| COF-ESGX2 | Coffret Epure Detox SuperGreen x2 | 125.60 | AVAILABLE |
| COFBEAUTEX2 | Coffret Beaute a la Chinoise x2 | 137.96 | AVAILABLE |
| COFMTC | Coffret Decouverte de la MTC | 88.90 | AVAILABLE |
| D084 | Anti-ivresse Hu Gan Jie Jiu Fang | 149.00 | AVAILABLE |
| MA284-YL | Aiguilles sans tube 0.35x60mm Yun Long | 2.90 | OUT_OF_STOCK |
| MA284X11-YL | Aiguilles sans tube 0.35x60mm x10 Yun Long | 29.00 | OUT_OF_STOCK |
| MA396-YL | Aiguilles couteau 0.50x40mm Yun Long | 18.80 | AVAILABLE |
| MA396X10-YL | Aiguilles couteau 0.50x40mm x10 Yun Long | 188.00 | AVAILABLE |
| MA399-YL | Aiguilles couteau 0.50x75mm Yun Long | 18.80 | AVAILABLE |
| MA399X10-YL | Aiguilles couteau 0.50x75mm x10 Yun Long | 188.00 | AVAILABLE |
| MA401-YL | Aiguilles couteau 0.60x50mm Yun Long | 18.80 | AVAILABLE |
| MA401X10-YL | Aiguilles couteau 0.60x50mm x10 Yun Long | 188.00 | AVAILABLE |
| MA403-YL | Aiguilles couteau 0.40x50mm Yun Long | 18.80 | AVAILABLE |
| MA403X10-YL | Aiguilles couteau 0.40x50mm x10 Yun Long | 188.00 | AVAILABLE |
| MA404-YL | Aiguilles couteau 0.40x25mm Yun Long | 18.80 | AVAILABLE |
| MA404X10-YL | Aiguilles couteau 0.40x25mm x10 Yun Long | 188.00 | AVAILABLE |
| MA644-TBCOUPE | Moxa superieur coupe Tongbai | 16.90 | AVAILABLE |
| MA644-TBMINI | Moxa superieur mini Tongbai | 20.90 | AVAILABLE |
| MA644-TBVRAC | Moxa superieur vrac Tongbai | 26.90 | AVAILABLE |
| MA645-NYBTN | Moxa essentiel batonnet Nanyang | 9.90 | AVAILABLE |
| MA645-NYCOUPE | Moxa essentiel coupe Nanyang | 8.90 | AVAILABLE |
| MA645-NYMINI | Moxa essentiel mini Nanyang | 11.90 | AVAILABLE |
| MA646-NYBTN | Moxa premium batonnet Nanyang | 48.90 | AVAILABLE |
| MA646-NYVRAC | Moxa premium vrac Nanyang | 16.90 | AVAILABLE |
| MA647-LHBTN | Moxa Lei Huo Jiu baton | 13.90 | AVAILABLE |
| MANDARINE | Cadeau echantillon peau de mandarine | 20.00 | AVAILABLE |
| OMAUF | Mauve fleur entiere bio 40g | 11.90 | AVAILABLE |
| OMAUFL | Mauve fleur entiere bio 100g | 24.90 | AVAILABLE |
| ... | _(et ~57 autres)_ | | |

</details>

### 32 produits presents UNIQUEMENT dans le CSV (supprimes du nouvel export)

La majorite sont en `out_of_stock` (29/32) — probablement retires du catalogue.

<details>
<summary>Liste complete des 32 produits retires</summary>

| ID | Titre | Prix | Statut |
|----|-------|:----:|:------:|
| D009 | Formule Sante des os | 38.90 EUR | out_of_stock |
| GLQ-01 | Filtre infuseur a the | 4.50 EUR | out_of_stock |
| MA111+MA412 | Kit moxibustion | 10.80 EUR | in_stock |
| MA162 | Gua sha corne de Buffle | 7.80 EUR | out_of_stock |
| MA164 | Gua sha corne de Buffle | 6.50 EUR | out_of_stock |
| MA165 | Gua sha corne de Yak | 7.40 EUR | out_of_stock |
| MA166 | Gua sha corne de Yak | 6.30 EUR | out_of_stock |
| MA167 | Gua sha corne de Yak | 7.50 EUR | out_of_stock |
| MA172+MA165+MA322 | Kit Ventouses Essentielles | 28.90 EUR | out_of_stock |
| MA181 | Tube de moxibustion | 3.40 EUR | out_of_stock |
| MA322 | Marteau fleur de prunier | 11.90 EUR | out_of_stock |
| MA352 | Aiguilles semi-permanentes | 30.90 EUR | out_of_stock |
| MA362+MA173+... | Kit Performance Acupuncture | 28.90 EUR | out_of_stock |
| MA413 | Boite de moxibustion sans fumee | 11.60 EUR | in_stock |
| MA633-MX3014+... | Kit Precision Acupuncture | 28.90 EUR | out_of_stock |
| MA642-MX3032 | Mini batonnets moxa adhesifs | 25.90 EUR | out_of_stock |
| MA643-MX3033-01 | Mini batonnets moxa faible fumee | 23.90 EUR | out_of_stock |
| MA653-MB5012 | Boite moxa bronze | 14.90 EUR | out_of_stock |
| MA711 | Balance traditionnelle chinoise | 12.90 EUR | out_of_stock |
| MA712 | Balance traditionnelle chinoise | 14.90 EUR | out_of_stock |
| MA724-04-GS5008 | Gua sha jade poisson | 9.60 EUR | out_of_stock |
| MA724-07-GS5018 | Roller visage jade | 9.30 EUR | out_of_stock |
| MA724-07-GS5018+... | Roller visage jade (kit) | 19.20 EUR | out_of_stock |
| MA725-04-GS7021 | Gua Sha Rose Quartz | 12.10 EUR | out_of_stock |
| MA731-04-GS4005 | Gua sha bois parfume | 8.30 EUR | out_of_stock |
| MA732-01-GS2001-01 | Massage bois palissandre | 8.30 EUR | out_of_stock |
| MA733-01-GS9008 | Gua sha bois de santal | 8.40 EUR | out_of_stock |
| MA751-2 | Stylo acupression palissandre | 6.70 EUR | out_of_stock |
| MA91X-MD4002 | Mannequin acupuncture cheval | 27.90 EUR | out_of_stock |
| MA91X-MD4005 | Mannequin acupuncture chat | 27.90 EUR | out_of_stock |
| MA97X-MD1003-01 | Modele acupuncture femme 48cm | 36.80 EUR | out_of_stock |
| MA97X-MD1004-04 | Modele acupuncture homme 60cm | 39.60 EUR | out_of_stock |

> 3 produits encore `in_stock` dans le CSV mais retires du XLSX : MA111+MA412, MA413, MA172+MA165+MA322

</details>

---

## 3. Differences de valeurs (sur les 1792 IDs communs)

### 3.1 Prix : 0 differences

Les prix sont **identiques** entre les deux fichiers pour tous les produits communs.

### 3.2 Disponibilite : 254 differences

| Changement | Nombre | Signification |
|------------|:------:|---------------|
| XLSX `AVAILABLE` → CSV `out_of_stock` | ~30 | Produits remis en stock dans le XLSX |
| XLSX `OUT_OF_STOCK` → CSV `in_stock` | ~180 | Produits devenus indisponibles dans le XLSX |
| XLSX `AVAILABLE_SOON` → CSV `out_of_stock` | ~44 | Nouveau statut "bientot disponible" dans le XLSX |

> **Impact important** : 254 produits (14%) ont change de statut de disponibilite. Le XLSX est plus recent et devrait etre la reference.

<details>
<summary>Exemples de changements de disponibilite</summary>

| ID | XLSX (nouveau) | CSV (actuel) |
|----|:--------------:|:------------:|
| MA553 | AVAILABLE | out_of_stock |
| MA553X11 | AVAILABLE | out_of_stock |
| CLQBDW | AVAILABLE_SOON | out_of_stock |
| CBFTCP | AVAILABLE_SOON | out_of_stock |
| OBOUL | OUT_OF_STOCK | in_stock |
| MA10128 | OUT_OF_STOCK | in_stock |
| MTCJZCS | OUT_OF_STOCK | in_stock |
| MA10093 | OUT_OF_STOCK | in_stock |

</details>

### 3.3 Titres : 452 differences

| Type de difference | Nombre |
|-------------------|:------:|
| Espaces en trop (double espace) | ~120 |
| Reformulation reelle du titre | ~332 |

**Exemples de reformulations significatives :**

| ID | XLSX (nouveau) | CSV (actuel) |
|----|----------------|--------------|
| MA553 | Aiguilles avec tube -0,25 x 40 mm - 500 aiguilles siliconees sans anneaux - Zhong Yan Tai He | 500 aiguilles avec tube -0,25 x 40 mm - 1 boite d'aiguilles siliconees |
| OCUMI | Carvi graine entiere bio - 1 Petit Sachet plante 50g | Cumin des Pres (Carvi) - 1 Petit Sachet plante 100g |
| OCUMIL | Carvi graine entiere bio - 1 Grand Sachet plante 200g | Cumin des Pres (Carvi) - 1 Grand Sachet plante 300g |

> Les titres du XLSX contiennent souvent le nom du fournisseur (Zhong Yan, Yun Long...) et certains produits ont ete renommes avec des poids differents (OCUMI : 50g vs 100g).

### 3.4 Descriptions : 1350 differences

| Situation | Nombre |
|-----------|:------:|
| Texte different (les deux remplis) | 1350 |
| Description dans XLSX seulement | 8 |
| Description dans CSV seulement | 32 |

> Le CSV utilise une description en texte brut. Le XLSX a un champ `description` (souvent vide/NaN) **mais** un champ `rich_text_description` avec du HTML structure. Ces deux sources sont complementaires.

### 3.5 Images : 146 differences

146 produits ont une URL d'image differente. Les URLs du XLSX pointent vers des versions plus recentes sur Cloudinary (timestamps plus recents dans les URLs).

### 3.6 Images additionnelles : 156 differences

156 produits ont des images additionnelles differentes entre les deux fichiers.

### 3.7 URLs : 17 differences

| Type | Nombre | Exemple |
|------|:------:|---------|
| Product ID different dans le parametre | ~10 | `?product=4790` vs `?product=474` |
| Slug de page different | ~7 | `/extrait-de-guarana-minceur-and-tonus-5230` vs `/guarana-4320` |

### 3.8 item_group_id : 13 differences

13 produits ont change de groupe entre les deux fichiers.

### 3.9 Sale price : 2 differences

| ID | XLSX | CSV |
|----|:----:|:---:|
| AYYRPCP | _(vide)_ | 34.11 EUR |
| AYYRCP | _(vide)_ | 34.11 EUR |

---

## 4. Donnees exclusives au XLSX (a exploiter pour ACP)

| Donnee | Remplissage | Impact ACP |
|--------|:-----------:|------------|
| `shipping_weight` | 1657/1886 (88%) | Remplir le champ `weight` + `item_weight_unit` |
| `rich_text_description` | 1399/1886 (74%) | Enrichir les descriptions produit |
| `category` | 1767/1886 (94%) | Affiner le champ `product_category` |
| Statut `AVAILABLE_SOON` | 44 produits | Nouveau statut non gere dans le CSV actuel |

---

## 5. Recommandations

### Priorite haute
1. **Ajouter les 94 nouveaux produits** du XLSX au feed ACP (72 sont en stock)
2. **Mettre a jour la disponibilite** de 254 produits selon le XLSX
3. **Mettre a jour les images** de 146 produits avec les nouvelles URLs
4. **Mettre a jour les URLs** de 17 produits

### Priorite moyenne
5. **Integrer `shipping_weight`** du XLSX pour remplir le champ `weight` ACP
6. **Integrer `rich_text_description`** pour enrichir les descriptions
7. **Integrer `category`** pour affiner les categories
8. **Mettre a jour les titres** (332 reformulations reelles)

### Priorite basse
9. **Retirer les 32 produits** absents du XLSX (29 deja out_of_stock)
10. **Gerer le statut `AVAILABLE_SOON`** (le mapper vers `preorder` ou `out_of_stock` dans ACP)
11. **Verifier les 13 changements de `item_group_id`**
