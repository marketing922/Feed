from fpdf import FPDF


class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "Comparaison GMC vs Export ERP - Laboratoire Calebasse", align="C")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title, level=1):
        if level == 1:
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(26, 54, 93)
            self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(43, 108, 176)
            self.set_line_width(0.8)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)
        elif level == 2:
            self.ln(4)
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(43, 108, 176)
            self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(190, 227, 248)
            self.set_line_width(0.4)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)
        elif level == 3:
            self.ln(2)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(44, 82, 130)
            self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(26, 26, 26)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def quote_text(self, text):
        self.set_fill_color(235, 248, 255)
        self.set_draw_color(43, 108, 176)
        x = self.get_x()
        y = self.get_y()
        self.set_line_width(0.8)
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(44, 82, 130)
        self.set_x(x + 6)
        self.multi_cell(180, 5.5, text, fill=True)
        self.line(x + 4, y, x + 4, self.get_y())
        self.ln(3)

    def add_table(self, headers, rows, col_widths=None):
        if not col_widths:
            total = 190
            col_widths = [total / len(headers)] * len(headers)

        # Header
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(43, 108, 176)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()

        # Rows
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(26, 26, 26)
        for row_idx, row in enumerate(rows):
            if self.get_y() > 265:
                self.add_page()
                self.set_font("Helvetica", "B", 9)
                self.set_fill_color(43, 108, 176)
                self.set_text_color(255, 255, 255)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
                self.ln()
                self.set_font("Helvetica", "", 8.5)
                self.set_text_color(26, 26, 26)

            if row_idx % 2 == 0:
                self.set_fill_color(247, 250, 252)
            else:
                self.set_fill_color(255, 255, 255)

            for i, cell in enumerate(row):
                align = "C" if i > 0 and len(headers) <= 5 else "L"
                self.cell(col_widths[i], 6, str(cell)[:60], border=1, fill=True, align=align)
            self.ln()
        self.ln(3)


pdf = PDFReport()
pdf.alias_nb_pages()
pdf.add_page()

# Title
pdf.section_title("Comparaison : GMC vs export-variants")
pdf.body_text(
    "Flux Google Merchant Center - Products source.xlsx (GMC) "
    "vs export-variants-2026-03-12.xlsx (Export ERP)"
)

# Resume global
pdf.section_title("Resume global", 2)
pdf.add_table(
    ["Metrique", "GMC", "Export ERP", "Ecart"],
    [
        ["Nombre de lignes", "1824", "1886", "+62"],
        ["Nombre de colonnes", "38", "13", "-25"],
        ["IDs uniques", "1824", "1886", "+62"],
        ["IDs en commun", "1792", "1792", "-"],
        ["IDs seulement dans GMC", "32", "-", "Produits retires"],
        ["IDs seulement dans Export ERP", "-", "94", "Nouveaux produits"],
    ],
    [60, 35, 35, 60],
)
# 1. Colonnes
pdf.section_title("1. Colonnes", 2)
pdf.section_title("Correspondance des colonnes", 3)
pdf.add_table(
    ["GMC (38 col.)", "Export ERP (13 col.)", "Match"],
    [
        ["id", "id", "Direct"],
        ["title", "title", "Direct"],
        ["description", "description", "Direct"],
        ["link", "url", "Renomme"],
        ["price", "price", "Direct"],
        ["sale price", "sale_price", "Renomme"],
        ["availability", "availability", "Format different"],
        ["image link", "image_link", "Renomme"],
        ["additional image link", "additional_image_link", "Renomme"],
        ["item group id", "item_group_id", "Renomme"],
        ["(absent)", "shipping_weight", "Exclusif Export ERP"],
        ["(absent)", "rich_text_description", "Exclusif Export ERP"],
        ["(absent)", "category", "Exclusif Export ERP"],
    ],
    [65, 65, 60],
)

pdf.section_title("3 colonnes exclusives au Export ERP", 3)
pdf.add_table(
    ["Colonne", "Remplissage", "Description"],
    [
        ["shipping_weight", "1657/1886 (88%)", "Poids en grammes"],
        ["rich_text_description", "1399/1886 (74%)", "Description HTML avec bullet points"],
        ["category", "1767/1886 (94%)", "Categories du site"],
    ],
    [50, 45, 95],
)

pdf.section_title("Colonnes exclusives au GMC (utiles)", 3)
pdf.add_table(
    ["Colonne", "Remplissage", "Utilite"],
    [
        ["gtin", "349/1824 (19%)", "Codes-barres EAN"],
        ["mpn", "1792/1824 (98%)", "Codes produit internes"],
        ["brand", "1792/1824 (98%)", "Laboratoire Calebasse"],
        ["condition", "1792/1824 (98%)", "new"],
        ["product_type", "1792/1824 (98%)", "Categories Google Shopping"],
        ["google_product_category", "~1700", "Code categorie Google"],
    ],
    [50, 45, 95],
)
pdf.quote_text(
    "Sur 28 colonnes exclusives au GMC, seulement 6 sont utiles. "
    "Les 22 autres sont vides ou non pertinentes."
)

# 2. Produits
pdf.add_page()
pdf.section_title("2. Produits (IDs)", 2)

pdf.section_title("94 produits seulement dans le Export ERP (nouveaux)", 3)
pdf.add_table(
    ["Statut", "Nombre"],
    [
        ["AVAILABLE", "72"],
        ["OUT_OF_STOCK", "17"],
        ["AVAILABLE_SOON", "5"],
    ],
    [95, 95],
)
pdf.body_text(
    "Principales categories : Aiguilles couteau Yun Long (~24), "
    "Aiguilles avec/sans tube Yun Long (~16), Moxa (~8), "
    "Coffrets et kits (~10), Plantes bio (~8), "
    "Formules et bundles (~12), Materiel divers (~8), Gruaux (~4)."
)

pdf.section_title("32 produits seulement dans le GMC (retires)", 3)
pdf.add_table(
    ["Statut", "Nombre"],
    [
        ["out_of_stock", "29"],
        ["in_stock", "3"],
    ],
    [95, 95],
)
pdf.quote_text(
    "3 produits in_stock retires : MA111+MA412 (Kit moxibustion), "
    "MA413 (Boite moxibustion), MA172+MA165+MA322 (Kit Ventouses). "
    "Probablement remplaces par de nouveaux IDs."
)

# 3. Differences de valeurs
pdf.section_title("3. Differences de valeurs (1792 IDs communs)", 2)

pdf.section_title("3.1 Prix : 0 differences", 3)
pdf.body_text("Les prix sont strictement identiques entre les deux fichiers.")

pdf.section_title("3.2 Sale price : 2 differences", 3)
pdf.add_table(
    ["ID", "GMC", "Export ERP"],
    [
        ["AYYRCP", "34.11", "(vide)"],
        ["AYYRPCP", "34.11", "(vide)"],
    ],
    [63, 63, 63],
)

pdf.section_title("3.3 Disponibilite : 254 differences (14%)", 3)
pdf.add_table(
    ["Changement", "Nombre", "Signification"],
    [
        ["in_stock -> OUT_OF_STOCK", "123", "Devenus indisponibles"],
        ["out_of_stock -> AVAILABLE_SOON", "92", "Bientot de retour"],
        ["out_of_stock -> AVAILABLE", "39", "Remis en stock"],
        ["Total", "254", ""],
    ],
    [65, 30, 95],
)
pdf.quote_text(
    "Le Export ERP introduit un nouveau statut AVAILABLE_SOON (92 produits) absent du GMC."
)

pdf.section_title("3.4 Titres : 452 differences", 3)
pdf.add_table(
    ["Type", "Nombre"],
    [
        ["Differences significatives", "172"],
        ["Differences mineures (espaces)", "280"],
        ["Total", "452"],
    ],
    [95, 95],
)

pdf.section_title("3.5 Descriptions", 3)
pdf.add_table(
    ["Situation", "Nombre"],
    [
        ["GMC rempli, Export ERP vide", "32"],
        ["GMC vide, Export ERP rempli", "8"],
        ["Les deux differents", "1389"],
        ["GMC total avec description", "1715 (96%)"],
        ["Export ERP total avec description", "1691 (90%)"],
    ],
    [95, 95],
)
pdf.quote_text(
    "Les descriptions sont complementaires : le GMC a du texte brut, "
    "le Export ERP a du HTML structure (rich_text_description)."
)

pdf.section_title("3.6-3.9 Autres differences", 3)
pdf.add_table(
    ["Champ", "Differences"],
    [
        ["Images", "146"],
        ["Images additionnelles", "156"],
        ["URLs", "17"],
        ["item_group_id", "13"],
    ],
    [95, 95],
)

# 4. Synthese
pdf.add_page()
pdf.section_title("4. Synthese : donnees exclusives", 2)

pdf.section_title("GMC apporte (et pas le Export ERP)", 3)
pdf.add_table(
    ["Donnee", "Valeur pour ACP"],
    [
        ["gtin (349 produits)", "Champ ACP gtin"],
        ["mpn (1792 produits)", "Champ ACP mpn"],
        ["brand (1792 produits)", "Champ ACP brand"],
        ["condition (1792 produits)", "Champ ACP condition"],
        ["product_type (1792 produits)", "Champ ACP product_category"],
        ["description texte (1715 produits)", "Champ ACP description"],
        ["sale price effective date (~50)", "sale_price_start/end_date"],
    ],
    [95, 95],
)

pdf.section_title("Export ERP apporte (et pas le GMC)", 3)
pdf.add_table(
    ["Donnee", "Valeur pour ACP"],
    [
        ["shipping_weight (1657 produits)", "Champ ACP weight"],
        ["rich_text_description (1399)", "Enrichir description"],
        ["category (1767 produits)", "Affiner product_category"],
        ["94 nouveaux produits", "Catalogue plus complet"],
        ["Statut AVAILABLE_SOON (92)", "Statut preorder ACP"],
        ["Disponibilite a jour", "254 changements"],
        ["Images plus recentes", "146 mises a jour"],
    ],
    [95, 95],
)

# 5. Recommandations
pdf.section_title("5. Recommandations", 2)
pdf.quote_text(
    "Les deux fichiers sont complementaires et non redondants. "
    "La strategie optimale pour le feed ACP est de fusionner les deux."
)
pdf.add_table(
    ["Source", "Donnees a prendre"],
    [
        [
            "GMC",
            "gtin, mpn, brand, condition, product_type, description, sale price effective date",
        ],
        [
            "Export ERP",
            "Catalogue (ref), disponibilite, titres, images, URLs, weight, rich_text_desc, category",
        ],
    ],
    [30, 160],
)
pdf.body_text(
    "C'est exactement ce que fait le script convert_to_acp.py actuel : "
    "il charge le GMC (via le CSV) comme base, puis fusionne le Export ERP "
    "par-dessus pour les donnees plus recentes."
)

output = "c:/Users/conta/Downloads/ACP/comparaison_GMC_vs_Export ERP.pdf"
pdf.output(output)
print(f"PDF genere: {output}")
