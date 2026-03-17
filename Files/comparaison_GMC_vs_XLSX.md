# Comparaison : Flux Google Merchant Center vs export-variants

> **Flux Google Merchant Center – Products source.xlsx** (GMC) vs **export-variants-2026-03-12.xlsx** (Export ERP)

---

## Resume global

| Metrique | GMC | Export ERP | Ecart |
|----------|:---:|:----:|:-----:|
| Nombre de lignes | 1824 | 1886 | +62 |
| Nombre de colonnes | 38 | 13 | -25 |
| IDs uniques | 1824 | 1886 | +62 |
| IDs en commun | 1792 | 1792 | - |
| IDs seulement dans GMC | **32** | - | Produits retires |
| IDs seulement dans Export ERP | - | **94** | Nouveaux produits |

---

## 1. Colonnes

### Correspondance des colonnes

| GMC (38 colonnes) | Export ERP (13 colonnes) | Match |
|--------------------|--------------------|:-----:|
| `id` | `id` | Direct |
| `title` | `title` | Direct |
| `description` | `description` | Direct |
| `link` | `url` | Renomme |
| `price` | `price` | Direct |
| `sale price` | `sale_price` | Renomme |
| `availability` | `availability` | Direct (format different) |
| `image link` | `image_link` | Renomme |
| `additional image link` | `additional_image_link` | Renomme |
| `item group id` | `item_group_id` | Renomme |
| _(absent)_ | `shipping_weight` | **Exclusif Export ERP** |
| _(absent)_ | `rich_text_description` | **Exclusif Export ERP** |
| _(absent)_ | `category` | **Exclusif Export ERP** |

### 3 colonnes exclusives au Export ERP

| Colonne | Remplissage | Description |
|---------|:-----------:|-------------|
| `shipping_weight` | 1657/1886 (88%) | Poids en grammes |
| `rich_text_description` | 1399/1886 (74%) | Description HTML avec bullet points |
| `category` | 1767/1886 (94%) | Categories du site (ex: "Bio, Digestion") |

### 28 colonnes exclusives au GMC

| Colonne | Remplissage | Utilite |
|---------|:-----------:|---------|
| `gtin` | 349/1824 (19%) | Codes-barres EAN |
| `mpn` | 1792/1824 (98%) | Codes produit internes (sku-XXX) |
| `brand` | 1792/1824 (98%) | "Laboratoire Calebasse" |
| `condition` | 1792/1824 (98%) | "new" |
| `product_type` | 1792/1824 (98%) | Categories Google Shopping |
| `identifier exists` | 1824/1824 | yes/no |
| `google_product_category` | ~1700 | Code categorie Google (ex: 1529) |
| `adult` | 1824/1824 | "no" |
| `availability date` | 0 | Vide |
| `expiration date` | 0 | Vide |
| `mobile link` | 0 | Vide |
| `sale price effective date` | ~50 | Periodes de promo |
| `product highlight` | 0 | Vide |
| `product detail` | 0 | Vide |
| `color` | 0 | Vide |
| `size` | 0 | Vide |
| `size type` | 0 | Vide |
| `size system` | 0 | Vide |
| `gender` | 0 | Vide |
| `material` | 0 | Vide |
| `pattern` | 0 | Vide |
| `age group` | 0 | Vide |
| `is bundle` | 0 | Vide |
| `unit pricing measure` | 0 | Vide |
| `unit pricing base measure` | 0 | Vide |
| `energy efficiency class` | 0 | Vide |
| `min energy efficiency class` | 0 | Vide |
| `sell on google quantity` | 0 | Vide |

> Sur 28 colonnes exclusives au GMC, seulement **6 sont utiles** (gtin, mpn, brand, condition, product_type, google_product_category). Les 22 autres sont vides ou non pertinentes.

---

## 2. Produits (IDs)

### 94 produits seulement dans le Export ERP (nouveaux)

| Statut | Nombre |
|--------|:------:|
| AVAILABLE | 72 |
| OUT_OF_STOCK | 17 |
| AVAILABLE_SOON | 5 |

**Principales categories :**
- Aiguilles couteau Yun Long (~24 refs)
- Aiguilles avec/sans tube Yun Long (~16 refs)
- Moxa premium/superieur/essentiel (~8 refs)
- Coffrets et kits (~10 refs)
- Plantes bio (eucalyptus, camomille, rose de Damas, mauve...) (~8 refs)
- Formules et bundles (~12 refs)
- Materiel divers (marteau, pilulier, bougie...) (~8 refs)
- Gruaux (~4 refs)
- Divers (mooncake, mandarine...) (~4 refs)

### 32 produits seulement dans le GMC (retires)

| Statut | Nombre |
|--------|:------:|
| out_of_stock | 29 |
| in_stock | 3 |

Majoritairement du materiel MTC en rupture : gua sha, balances, mannequins, kits, etc.

> Les 3 produits in_stock retires : MA111+MA412 (Kit moxibustion), MA413 (Boite moxibustion), MA172+MA165+MA322 (Kit Ventouses). Probablement remplaces par de nouveaux IDs dans le Export ERP.

---

## 3. Differences de valeurs (1792 IDs communs)

### 3.1 Prix : 0 differences

Les prix sont **strictement identiques** entre les deux fichiers. Format identique (numerique sans devise).

### 3.2 Sale price : 2 differences

| ID | GMC | Export ERP |
|----|:---:|:----:|
| AYYRCP | 34.11 | _(vide)_ |
| AYYRPCP | 34.11 | _(vide)_ |

> Le Export ERP ne contient plus ces promotions.

### 3.3 Disponibilite : 254 differences (14%)

| Changement | Nombre | Signification |
|------------|:------:|---------------|
| `in_stock` (GMC) -> `OUT_OF_STOCK` (Export ERP) | 123 | Produits devenus indisponibles |
| `out_of_stock` (GMC) -> `AVAILABLE_SOON` (Export ERP) | 92 | Produits bientot de retour |
| `out_of_stock` (GMC) -> `AVAILABLE` (Export ERP) | 39 | Produits remis en stock |
| **Total** | **254** | |

> Le Export ERP introduit un nouveau statut `AVAILABLE_SOON` (92 produits) qui n'existe pas dans le GMC. Cela concerne des produits actuellement `out_of_stock` dans le GMC qui seront bientot disponibles.

### 3.4 Titres : 452 differences

| Type | Nombre |
|------|:------:|
| Differences significatives (reformulation, renommage, poids) | 172 |
| Differences mineures (espaces, tirets, ponctuation) | 280 |
| **Total** | **452** |

**Exemples de reformulations significatives :**

| ID | GMC | Export ERP |
|----|-----|------|
| OCUMI | Cumin des Pres (Carvi) - 1 Petit Sachet plante 100g | Carvi graine entiere bio - 1 Petit Sachet plante 50g |
| MA553 | 500 aiguilles avec tube -0,25 x 40 mm - 1 boite d'aiguilles | Aiguilles avec tube -0,25 x 40 mm - 500 aiguilles siliconees sans anneaux - Zhong Yan Tai He |

> Certains produits ont change de nom ET de poids (OCUMI: 100g -> 50g, OCUMIL: 300g -> 200g).

### 3.5 Descriptions : differences majeures

| Situation | Nombre |
|-----------|:------:|
| GMC a description, Export ERP vide | 32 |
| GMC vide, Export ERP a description | 8 |
| Les deux remplis mais differents | 1389 |
| GMC total avec description | 1715 (96%) |
| Export ERP total avec description | 1691 (90%) |

> Les descriptions sont tres differentes entre les deux fichiers. Le GMC contient des descriptions textuelles classiques. Le Export ERP a un champ `description` souvent vide mais un champ `rich_text_description` avec du HTML structure (bullet points). Les deux sont **complementaires**.

### 3.6 Images : 146 differences

Les images du Export ERP sont plus recentes (timestamps Cloudinary plus eleves). Certains produits ont ete re-photographies.

### 3.7 Images additionnelles : 156 differences

Le Export ERP contient davantage d'images additionnelles.

### 3.8 URLs : 17 differences

Principalement des changements de slug de page ou de parametres `?product=`.

### 3.9 item_group_id : 13 differences

13 produits ont change de groupe (reorganisation catalogue).

---