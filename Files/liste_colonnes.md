# ACP OpenAI - Liste des 77 colonnes

## OpenAI Flags (2)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 1 | `is_eligible_search` | 🔴 Required | Active la visibilite du produit dans la recherche ChatGPT |
| 2 | `is_eligible_checkout` | 🔴 Required | Active l'achat direct dans ChatGPT (necessite privacy policy et TOS) |

## Basic Product Data (6)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 3 | `item_id` | 🔴 Required | Identifiant unique du produit/variante (max 100 chars, stable dans le temps) |
| 4 | `gtin` | Optional | Code-barres international (EAN/UPC, 8-14 chiffres, sans tirets) |
| 5 | `mpn` | Optional | Reference fabricant (max 70 chars) |
| 6 | `title` | 🔴 Required | Nom du produit (max 150 chars, UTF-8, eviter les majuscules) |
| 7 | `description` | 🔴 Required | Description complete du produit (max 5000 chars, texte brut) |
| 8 | `url` | 🔴 Required | URL de la page produit (doit repondre HTTP 200, HTTPS recommande) |

## Item Information (13)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 9 | `brand` | 🔴 Required | Nom de la marque (max 70 chars) |
| 10 | `condition` | Optional | Etat du produit (ex: "new", en minuscules) |
| 11 | `product_category` | Optional | Categorie produit avec separateur ">" (ex: Sante > Plantes > Tisanes) |
| 12 | `material` | Optional | Materiau principal du produit (max 100 chars) |
| 13 | `dimensions` | Optional | Dimensions au format LxWxH + unite (ex: "10x5x3 cm") |
| 14 | `length` | Optional | Longueur (si dimensions non utilise) |
| 15 | `width` | Optional | Largeur (si dimensions non utilise) |
| 16 | `height` | Optional | Hauteur (si dimensions non utilise) |
| 17 | `dimensions_unit` | Conditionnel | Unite des dimensions : "in" ou "cm" (requis si dimensions renseignees) |
| 18 | `weight` | Optional | Poids du produit |
| 19 | `item_weight_unit` | Conditionnel | Unite de poids : "lb" ou "kg" (requis si weight renseigne) |
| 20 | `age_group` | Optional | Tranche d'age : newborn, infant, toddler, kids, adult |

## Media (4)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 21 | `image_url` | 🔴 Required | URL de l'image principale (JPEG/PNG, HTTPS recommande) |
| 22 | `additional_image_urls` | Optional | URLs d'images supplementaires, separees par des virgules |
| 23 | `video_url` | Optional | URL de video produit (accessible publiquement) |
| 24 | `model_3d_url` | Optional | URL d'un modele 3D (format GLB/GLTF recommande) |

## Price & Promotions (6)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 25 | `price` | 🔴 Required | Prix de vente normal + devise ISO 4217 (ex: "9.40 EUR") |
| 26 | `sale_price` | Optional | Prix promo (doit etre <= price, meme format) |
| 27 | `sale_price_start_date` | Optional | Debut de la promo (ISO 8601) |
| 28 | `sale_price_end_date` | Optional | Fin de la promo (ISO 8601) |
| 29 | `unit_pricing_measure` | Optional | Mesure de prix unitaire (ex: "100g") - necessite base_measure |
| 30 | `pricing_trend` | Optional | Tendance du prix (max 80 chars) |

## Availability & Inventory (5)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 31 | `availability` | 🔴 Required | Statut stock : in_stock, out_of_stock, pre_order, backorder, unknown |
| 32 | `availability_date` | Conditionnel | Date de disponibilite ISO 8601 (requis si pre_order) |
| 33 | `expiration_date` | Optional | Date d'expiration, le produit est retire apres cette date |
| 34 | `pickup_method` | Optional | Mode retrait : in_store, reserve, not_supported |
| 35 | `pickup_sla` | Optional | Delai de retrait (necessite pickup_method) |

## Variants (14)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 36 | `group_id` | 🔴 Required | Identifiant du groupe de variantes (max 70 chars) |
| 37 | `listing_has_variations` | 🔴 Required | Indique si le produit a des variantes (true/false) |
| 38 | `variant_dict` | Recommande | Objet JSON decrivant les variantes (ex: {"format": "Sachet", "poids": "100g"}) |
| 39 | `item_group_title` | Optional | Titre commun au groupe de variantes (max 150 chars) |
| 40 | `color` | Optional | Couleur du produit (max 40 chars) |
| 41 | `size` | Recommande | Taille du produit (max 20 chars) |
| 42 | `size_system` | Recommande | Systeme de taille, code pays ISO 3166 (ex: FR) |
| 43 | `gender` | Optional | Genre cible (en minuscules) |
| 44 | `offer_id` | Optional | Identifiant unique de l'offre dans le flux |
| 45 | `custom_variant1_category` | Optional | Nom de la dimension de variante personnalisee 1 (ex: "Format") |
| 46 | `custom_variant1_option` | Optional | Valeur de la variante personnalisee 1 (ex: "Petit Sachet") |
| 47 | `custom_variant2_category` | Optional | Nom de la dimension de variante personnalisee 2 (ex: "Poids") |
| 48 | `custom_variant2_option` | Optional | Valeur de la variante personnalisee 2 (ex: "100g") |
| 49 | `custom_variant3_category` | Optional | Nom de la dimension de variante personnalisee 3 |
| 50 | `custom_variant3_option` | Optional | Valeur de la variante personnalisee 3 |

## Fulfillment (2)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 51 | `shipping` | Optional | Infos livraison au format "pays:region:service:prix:delai" (separateur " : ") |
| 52 | `is_digital` | Optional | Produit numerique (true/false) |

## Merchant Info (5)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 53 | `seller_name` | 🔴 Required | Nom du vendeur (max 70 chars) |
| 54 | `marketplace_seller` | Optional | Vendeur tiers sur marketplace (max 70 chars) |
| 55 | `seller_url` | 🔴 Required | URL de la boutique du vendeur |
| 56 | `seller_privacy_policy` | Conditionnel | URL politique de confidentialite (requis si checkout active) |
| 57 | `seller_tos` | Conditionnel | URL des CGV (requis si checkout active) |

## Returns (4)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 58 | `accepts_returns` | Optional | Accepte les retours (true/false) |
| 59 | `return_deadline_in_days` | Optional | Delai de retour en jours (entier positif) |
| 60 | `accepts_exchanges` | Optional | Accepte les echanges (true/false) |
| 61 | `return_policy` | 🔴 Required | URL de la politique de retour |

## Performance Signals (2)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 62 | `popularity_score` | Optional | Score de popularite (echelle 0-5) |
| 63 | `return_rate` | Optional | Taux de retour (0-100%) |

## Compliance (2)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 64 | `warning` | Recommande | Avertissements reglementaires sur le produit |
| 65 | `age_restriction` | Recommande | Age minimum d'achat (entier positif) |

## Reviews & Q&A (6)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 66 | `review_count` | Optional | Nombre d'avis clients (entier >= 0) |
| 67 | `star_rating` | Optional | Note moyenne du produit (echelle 0-5) |
| 68 | `store_review_count` | Optional | Nombre d'avis sur la boutique (entier >= 0) |
| 69 | `store_star_rating` | Optional | Note moyenne de la boutique (echelle 0-5) |
| 70 | `q_and_a` | Recommande | Questions/reponses au format JSON : [{"q": "...", "a": "..."}] |
| 71 | `reviews` | Recommande | Avis clients au format JSON : [{"title": "...", "content": "...", "rating": 5}] |

## Related Products (2)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 72 | `related_product_id` | Recommande | IDs de produits lies, separes par des virgules |
| 73 | `relationship_type` | Recommande | Type de relation : part_of_set, required_part, often_bought_with, substitute, different_brand, accessory |

## Geo Tagging (4)

| # | Colonne | Statut | Description |
|---|---------|--------|-------------|
| 74 | `target_countries` | 🔴 Required | Pays cibles, codes ISO 3166-1 alpha-2 (ex: FR) |
| 75 | `store_country` | 🔴 Required | Pays du vendeur, code ISO 3166-1 alpha-2 |
| 76 | `geo_price` | Optional | Prix specifique par region + devise ISO 4217 |
| 77 | `geo_availability` | Optional | Disponibilite par region (format: "statut (region)") |

---

## Checklist Required (19 colonnes)

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 1 | `is_eligible_search` | [x] | 1824/1824 | Valeur: true |
| 2 | `is_eligible_checkout` | [x] | 1824/1824 | Valeur: true |
| 3 | `item_id` | [x] | 1824/1824 | Depuis id Google Shopping |
| 6 | `title` | [x] | 1824/1824 | Depuis title Google Shopping |
| 7 | `description` | [x] | 1740/1824 | 84 produits sans description |
| 8 | `url` | [x] | 1824/1824 | Depuis link Google Shopping |
| 9 | `brand` | [x] | 1824/1824 | Laboratoire Calebasse |
| 21 | `image_url` | [x] | 1824/1824 | Depuis image link Google Shopping |
| 25 | `price` | [x] | 1824/1824 | Format corrige: "9.40 EUR" |
| 31 | `availability` | [x] | 1824/1824 | in_stock / out_of_stock |
| 36 | `group_id` | [x] | 1824/1824 | Depuis item group id Google Shopping |
| 37 | `listing_has_variations` | [x] | 1824/1824 | Auto-detecte (1410 true / 414 false) |
| 53 | `seller_name` | [x] | 1824/1824 | Laboratoire Calebasse |
| 55 | `seller_url` | [x] | 1824/1824 | https://calebasse.com |
| 56 | `seller_privacy_policy` | [x] | 1824/1824 | https://calebasse.com/politique-confidentialite |
| 57 | `seller_tos` | [x] | 1824/1824 | https://calebasse.com/cgv |
| 61 | `return_policy` | [x] | 1824/1824 | https://calebasse.com/cgv |
| 74 | `target_countries` | [x] | 1824/1824 | FR |
| 75 | `store_country` | [x] | 1824/1824 | FR |

**Required : 19/19 remplis (100%)** - 84 descriptions manquantes a completer

---

## Checklist Recommande (10 colonnes)

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 38 | `variant_dict` | [x] | 1313/1824 | JSON auto-genere depuis le titre (format + poids) |
| 41 | `size` | [ ] | 0/1824 | Non applicable (plantes, pas du textile) |
| 42 | `size_system` | [ ] | 0/1824 | Non applicable |
| 64 | `warning` | [x] | 1824/1824 | Avertissement standard : enfants < 12 ans, femmes enceintes, dose journaliere |
| 65 | `age_restriction` | [x] | 1824/1824 | Valeur: 12 (ans minimum) |
| 70 | `q_and_a` | [x] | 1824/1824 | 10 FAQ extraites de calebasse.com/faq (preparation, traitement, livraison...) |
| 71 | `reviews` | [ ] | 0/1824 | Non disponible (le site n'expose que la note, pas le texte des avis) |
| 72 | `related_product_id` | [x] | 238/1824 | 87 groupes scrapes via "La Calebasse vous conseille", ~8 produits lies chacun |
| 73 | `relationship_type` | [x] | 238/1824 | Valeur: often_bought_with |

**Recommande : 6/10 remplis (60%)** - 2 non applicables (size), 2 non disponibles (reviews)

---

## Checklist Optional (48 colonnes)

### Basic Product Data

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 4 | `gtin` | [x] | 349/1824 | Code EAN renseigne pour 349 produits |
| 5 | `mpn` | [x] | 1824/1824 | Format: sku-XXX |

### Item Information

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 10 | `condition` | [x] | 1824/1824 | Valeur: new |
| 11 | `product_category` | [x] | 1824/1824 | Sante & Bien-etre > Plantes & Herbes > ... |
| 12 | `material` | [ ] | 0/1824 | Non applicable pour des plantes |
| 13 | `dimensions` | [ ] | 0/1824 | Non applicable |
| 14 | `length` | [ ] | 0/1824 | Non applicable |
| 15 | `width` | [ ] | 0/1824 | Non applicable |
| 16 | `height` | [ ] | 0/1824 | Non applicable |
| 17 | `dimensions_unit` | [ ] | 0/1824 | Non applicable (conditionnel si dimensions) |
| 18 | `weight` | [x] | 1298/1824 | Extrait du titre (en grammes) |
| 19 | `item_weight_unit` | [x] | 1298/1824 | Valeur: g |
| 20 | `age_group` | [ ] | 0/1824 | Non renseigne |

### Media

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 22 | `additional_image_urls` | [x] | 73/1824 | 73 produits avec images supplementaires |
| 23 | `video_url` | [ ] | 0/1824 | Pas de videos produit sur le site |
| 24 | `model_3d_url` | [ ] | 0/1824 | Pas de modeles 3D |

### Price & Promotions

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 26 | `sale_price` | [x] | 50/1824 | 50 produits en promotion |
| 27 | `sale_price_start_date` | [ ] | 0/1824 | Pas de dates de promo dans le flux source |
| 28 | `sale_price_end_date` | [ ] | 0/1824 | Pas de dates de promo dans le flux source |
| 29 | `unit_pricing_measure` | [ ] | 0/1824 | Non renseigne |
| 30 | `pricing_trend` | [ ] | 0/1824 | Non renseigne |

### Availability & Inventory

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 32 | `availability_date` | [ ] | 0/1824 | Conditionnel: requis si pre_order |
| 33 | `expiration_date` | [ ] | 0/1824 | Non renseigne |
| 34 | `pickup_method` | [x] | 1824/1824 | Valeur: in_store (boutique 15 rue de la Vistule, Paris 13) |
| 35 | `pickup_sla` | [ ] | 0/1824 | Delai de retrait non renseigne |

### Variants

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 39 | `item_group_title` | [x] | 1824/1824 | Auto-genere depuis le titre (nom FR - nom CN) |
| 40 | `color` | [ ] | 0/1824 | Non applicable |
| 43 | `gender` | [ ] | 0/1824 | Non applicable |
| 44 | `offer_id` | [ ] | 0/1824 | Non renseigne |
| 45 | `custom_variant1_category` | [x] | 1824/1824 | Valeur: Format |
| 46 | `custom_variant1_option` | [x] | 1288/1824 | Petit Sachet, Grand Sachet, Poudre concentree, Gelules... |
| 47 | `custom_variant2_category` | [x] | 1824/1824 | Valeur: Poids |
| 48 | `custom_variant2_option` | [x] | 1298/1824 | 50g, 100g, 200g, 300g... |
| 49 | `custom_variant3_category` | [ ] | 0/1824 | Non utilise |
| 50 | `custom_variant3_option` | [ ] | 0/1824 | Non utilise |

### Fulfillment

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 51 | `shipping` | [x] | 1824/1824 | FR:::0.00 EUR:2-5 days |
| 52 | `is_digital` | [x] | 1824/1824 | Valeur: false |

### Merchant Info

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 54 | `marketplace_seller` | [ ] | 0/1824 | Non applicable (vente directe) |

### Returns

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 58 | `accepts_returns` | [x] | 1824/1824 | Valeur: true |
| 59 | `return_deadline_in_days` | [x] | 1824/1824 | Valeur: 14 |
| 60 | `accepts_exchanges` | [x] | 1824/1824 | Valeur: true |

### Performance Signals

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 62 | `popularity_score` | [ ] | 0/1824 | Non renseigne (echelle 0-5) |
| 63 | `return_rate` | [ ] | 0/1824 | Non renseigne (0-100%) |

### Reviews & Q&A

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 66 | `review_count` | [ ] | 0/1824 | Non disponible (note aggregate seulement) |
| 67 | `star_rating` | [ ] | 0/1824 | Non disponible |
| 68 | `store_review_count` | [ ] | 0/1824 | Non renseigne |
| 69 | `store_star_rating` | [ ] | 0/1824 | Non renseigne |

### Geo Tagging

| # | Colonne | Rempli | Produits | Notes |
|---|---------|--------|----------|-------|
| 76 | `geo_price` | [ ] | 0/1824 | Non renseigne (pas de prix par region) |
| 77 | `geo_availability` | [ ] | 0/1824 | Non renseigne |

**Optional : 19/48 remplis (40%)** - 29 vides (majorite non applicables)

---

## Resume global

| Categorie | Remplis | Total | Taux |
|-----------|---------|-------|------|
| 🟢 **Required** | **19** | **19** | **100%** |
| Recommande | 6 | 10 | 60% |
| Optional | 19 | 48 | 40% |
| **Total** | **44** | **77** | **57%** |

### Statistiques detaillees

| Metrique | Valeur |
|----------|--------|
| Produits totaux | 1824 |
| Produits avec variations | 1410 (77%) |
| Produits sans variations | 414 (23%) |
| Produits avec GTIN/EAN | 349 (19%) |
| Produits avec description | 1740 (95%) |
| Produits avec sale_price | 50 (3%) |
| Produits avec images supplementaires | 73 (4%) |
| Produits avec poids extrait | 1298 (71%) |
| Produits avec variant_dict | 1313 (72%) |
| Produits avec related_product_id | 238 (13%) |
| Groupes de produits scrapes (related) | 87 |

### Colonnes non applicables (produits = plantes medicinales)

- `material`, `dimensions`, `length`, `width`, `height`, `dimensions_unit` (pas de dimensions physiques pertinentes)
- `color`, `gender`, `size`, `size_system` (pas de variantes textile)
- `video_url`, `model_3d_url` (pas de media enrichi)
- `marketplace_seller` (vente directe uniquement)
- `geo_price`, `geo_availability` (prix unique, pas de variation regionale)

### Priorites restantes

1. **84 descriptions manquantes** - Completer les produits sans description (95% -> 100%)
2. **related_product_id** - Scraper les ~413 pages produit restantes pour passer de 238 a ~1824 produits (13% -> ~100%)
3. **reviews** - Integrer les avis clients si donnees disponibles depuis le back-office (note + texte)
4. **1475 GTIN manquants** - Completer les codes EAN pour les produits qui en ont (19% -> potentiellement plus)
