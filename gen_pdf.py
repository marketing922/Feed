"""Genere un PDF propre de la comparaison ERP vs GMC."""
from fpdf import FPDF
import os

class Report(FPDF):
    def header(self):
        self.set_font("Arial", "B", 10)
        self.set_text_color(137, 184, 50)
        self.cell(0, 6, "Laboratoire Calebasse", align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section(self, title):
        self.set_font("Arial", "B", 13)
        self.set_text_color(26, 26, 26)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(137, 184, 50)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            usable = self.w - self.l_margin - self.r_margin
            col_widths = [usable / len(headers)] * len(headers)
        # Header
        self.set_font("Arial", "B", 8)
        self.set_fill_color(137, 184, 50)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()
        # Rows
        self.set_font("Arial", "", 8)
        self.set_text_color(26, 26, 26)
        for ri, row in enumerate(rows):
            bg = ri % 2 == 1
            if bg:
                self.set_fill_color(245, 245, 243)
            h = 6
            for i, val in enumerate(row):
                self.cell(col_widths[i], h, str(val)[:80], border=1, fill=bg, align="C" if i == 0 else "L")
            self.ln()

    def sku_block(self, skus, label=""):
        if label:
            self.set_font("Arial", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Arial", "", 7)
        self.set_text_color(60, 60, 60)
        text = ", ".join(skus)
        self.multi_cell(0, 4, text)
        self.ln(2)


pdf = Report()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# Use Windows Arial TTF for Unicode support
font_dir = "C:/Windows/Fonts"
pdf.add_font("Arial", "", os.path.join(font_dir, "arial.ttf"), uni=True)
pdf.add_font("Arial", "B", os.path.join(font_dir, "arialbd.ttf"), uni=True)
pdf.add_font("Arial", "I", os.path.join(font_dir, "ariali.ttf"), uni=True)

pdf.add_page()

# Title
pdf.set_font("Arial", "B", 22)
pdf.set_text_color(137, 184, 50)
pdf.cell(0, 14, "Comparaison ERP vs GMC", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Arial", "", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, "12 mars 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)

# --- Vue d'ensemble ---
pdf.section("Vue d'ensemble")
pdf.table(
    ["", "ERP", "GMC"],
    [
        ["Total SKUs", "1886", "1824"],
        ["Colonnes", "12", "38"],
        ["SKUs communs", "1790", "1790"],
        ["Nouveaux (ERP seul)", "96", "\u2014"],
        ["A retirer (GMC seul)", "\u2014", "34"],
    ],
    [60, 55, 55],
)
pdf.ln(4)

# --- Resume des differences ---
pdf.section("Differences sur les 1790 SKUs communs")
pdf.table(
    ["Champ", "Nb differences"],
    [
        ["Description", "134"],
        ["Titre", "161"],
        ["Disponibilite", "254"],
        ["Image link", "146"],
        ["Additional image link", "156"],
        ["URL / link", "17"],
        ["Item group id", "13"],
        ["Sale price", "2"],
        ["Prix", "0"],
    ],
    [80, 50],
)
pdf.ln(4)

# --- Description ---
pdf.section("1. Description \u2014 134 differences")
pdf.set_font("Arial", "", 8)
pdf.set_text_color(26, 26, 26)
pdf.multi_cell(0, 5, "Les descriptions ERP ont ete mises a jour (nouveau contenu, bienfaits reformules). 5 exemples :")
pdf.ln(2)
desc_examples = [
    ["ACP", "Au parfum delicatement acidule...", "Pour apaiser les voies respiratoires..."],
    ["BASC", "Un rituel apaisant a adopter...", "Pour retrouver des nuits sereines..."],
    ["D035", "Formule sans melatonine... (espace)", "Formule sans melatonine..."],
    ["MA644", "Issu des monts Tongbai...", "Pour ameliorer la circulation..."],
    ["OCANP", "Reconfortante et protectrice...", "Reconfortante et protectrice... (espace)"],
]
pdf.table(["SKU", "ERP (extrait)", "GMC (extrait)"], desc_examples, [20, 75, 75])
pdf.ln(2)
pdf.sku_block([
    "ACPCP","ACPGL","ACPL","ACPLX2","ADS","ADSCP","ADSGL","ADSL","AGQZ","AGQZL",
    "AHGQ-XL","AHHUA","AHHUACP","AHHUAGL","AHJTCP","AHJTGL","AHRS","AHSHGL","AHSW","AHSWL",
    "AJHUA","AJHUAL","AJQC","AJQCCP","AJQCGL","AJQCL","AKS","AKSL","ALZ","ALZCP",
    "ALZGL","ALZL","ALZX","AMGH","AMGHL","AMLH","AMLHL","AMLHLX2","ARS","ARSX2",
    "ASFCK","ASFHO","ASFHO-BIO","ASUDH","ASUDHCP","ASUDHGL","ASUDHL","ASW","ASWL","ASYECP",
    "ASYEGL","AXG","AXGX3","AYCHUA","AYYR","AYYRCP","AYYRGL","AYYRL","AYYRPCP","et 70 autres..."
], "129 autres SKUs concernes :")

# --- Titre ---
pdf.section("2. Titre \u2014 161 differences")
pdf.set_font("Arial", "", 8)
pdf.set_text_color(26, 26, 26)
pdf.multi_cell(0, 5, "Corrections orthographiques, reformulations, changements de denomination. 5 exemples :")
pdf.ln(2)
title_examples = [
    ["ABZS", "Rhizome d'Atractylode...", "Rhizome d'Atracylode... (typo)"],
    ["ACPXH", "...Chen pi (Xinhui)...", "...Cheng pi (Xinhui)..."],
    ["AGQZ", "Baies de Goji premium...", "Baies de Goji (Gou qi zi)..."],
    ["AHGQ", "Baies de Goji Noires premium...", "Baies de Goji noir premium..."],
    ["ALCGL", "...poudre mouluee 50g", "...poudre concentree 50g"],
]
pdf.table(["SKU", "ERP", "GMC"], title_examples, [20, 75, 75])
pdf.ln(2)
pdf.sku_block([
    "ABZSCP","ABZSGL","ABZSL","AGQZL","AHGQ-XL","AHJT","AHJTL","AHP","AHPL","ALZ",
    "ALZCP","ALZGL","ALZL","AMGH","AMGHL","AMLH","AMLHL","AMLHLX2","ASFHO-BIO","AWJP",
    "AWJPL","AYCHUA","AYYRCP","BASCX3","BBQSSB","BBQSSBL","BQSZMB","BQSZMBL","BSMT3",
    "et 127 autres..."
], "156 autres SKUs concernes :")

# --- Disponibilite ---
pdf.section("3. Disponibilite \u2014 254 differences")
pdf.table(
    ["Changement", "ERP", "GMC", "Nb SKUs"],
    [
        ["Epuise ERP, en stock GMC", "OUT_OF_STOCK", "in_stock", "123"],
        ["Bientot dispo ERP, epuise GMC", "AVAILABLE_SOON", "out_of_stock", "92"],
        ["Dispo ERP, epuise GMC", "AVAILABLE", "out_of_stock", "39"],
    ],
    [55, 40, 40, 25],
)
pdf.ln(4)

# --- Image link ---
pdf.section("4. Image link \u2014 146 differences")
pdf.set_font("Arial", "", 8)
pdf.set_text_color(26, 26, 26)
pdf.multi_cell(0, 5, "146 SKUs ont une image principale differente entre l'ERP et le GMC.")
pdf.ln(2)

# --- Additional image link ---
pdf.section("5. Additional image link \u2014 156 differences")
pdf.set_font("Arial", "", 8)
pdf.set_text_color(26, 26, 26)
pdf.multi_cell(0, 5, "156 SKUs ont des images additionnelles differentes.")
pdf.ln(2)

# --- URL ---
pdf.section("6. URL / link \u2014 17 differences")
pdf.table(
    ["SKU", "Motif"],
    [
        ["AHJTCP/GL", "Slug produit change (5251 vs 3830)"],
        ["AJQCCP/GL", "Slug produit change (ajout suffixe)"],
        ["AKS/CP/GL/L", "Slug produit change (5213 vs 3847)"],
        ["ASYECP/GL", "Slug produit change (5248 vs 3908)"],
        ["AYYRCP", "Slug produit change (5221 vs 3951)"],
        ["OGUARGL", "Slug produit change (5230 vs 4320)"],
        ["ASFHO-BIO", "product= id different (7649 vs 7592)"],
        ["AXYHL", "product= id different (4790 vs 474)"],
        ["OMURF/L", "product= id different (7512 vs 4648)"],
        ["XJYD", "Slug produit change (4790 vs 474)"],
    ],
    [35, 120],
)
pdf.ln(2)

# --- Item group id ---
pdf.section("7. Item group id \u2014 13 differences")
pdf.table(
    ["SKU", "ERP", "GMC"],
    [
        ["AHJTCP", "5251", "3830"],
        ["AHJTGL", "5251", "3830"],
        ["AJQCCP", "5250", "3799"],
        ["AJQCGL", "5250", "3799"],
        ["AKS", "5213", "3847"],
        ["AKSL", "5213", "3847"],
        ["ASYECP", "5248", "3908"],
        ["ASYEGL", "5248", "3908"],
        ["AYYRCP", "5221", "3951"],
        ["COF-VEC", "5235", "4367"],
        ["COFBEAUTE", "5231", "4367"],
        ["OGUARGL", "5230", "4320"],
        ["XJYD", "4790", "474"],
    ],
    [35, 40, 40],
)
pdf.ln(2)

# --- Sale price ---
pdf.section("8. Sale price \u2014 2 differences")
pdf.table(
    ["SKU", "ERP", "GMC"],
    [
        ["AYYRCP", "(vide)", "34.11"],
        ["AYYRPCP", "(vide)", "34.11"],
    ],
    [35, 40, 40],
)
pdf.ln(2)

# --- Nouveaux et retires (compact) ---
pdf.section("9. Nouveaux SKUs \u2014 96 produits")
pdf.set_font("Arial", "", 8)
pdf.set_text_color(26, 26, 26)
pdf.multi_cell(0, 5, "96 produits presents dans l'ERP mais absents du GMC. Ils seront ajoutes automatiquement lors de la mise a jour.")
pdf.ln(2)

pdf.section("10. SKUs a retirer \u2014 34 produits")
pdf.set_font("Arial", "", 8)
pdf.set_text_color(26, 26, 26)
pdf.multi_cell(0, 5, "34 produits presents dans le GMC mais absents de l'ERP. Ils seront deplaces dans l'onglet 'Retires'.")
pdf.ln(2)
pdf.sku_block([
    "BK4114-02","D009","GLQ-01","MA111+MA412","MA162","MA164","MA165","MA166","MA167",
    "MA172+MA165+MA322","MA181","MA322","MA352","MA362+MA173+MA553+MA322+ZJYPB",
    "MA413","MA633+MA553+MA173+ZJYPB","MA642-MX3032","MA643-MX3033-01","MA653-MB5012",
    "MA711","MA712","MA724-04-GS5008","MA724-07-GS5018","MA724-07+MA724-01",
    "MA725-04-GS7021","MA731-04-GS4005","MA732-01-GS2001-01","MA733-01-GS9008",
    "MA751-2","MA91X-MD4002","MA91X-MD4005","MA97X-MD1003-01","MA97X-MD1004-04","MTC-SYQ-2"
], "SKUs concernes :")

out = os.path.join(os.path.dirname(__file__), "comparaison_ERP_vs_GMC.pdf")
pdf.output(out)
print(f"PDF genere : {out}")
