# Calebasse Feed Manager

Outil de mise a jour automatique des feeds produits **ACP OpenAI** et **Google Merchant Center** pour le [Laboratoire Calebasse](https://calebasse.com) (medecine traditionnelle chinoise).

## Fonctionnalites

- **Import ERP** : Importer un fichier `export-variants.xlsx` depuis l'ERP pour mettre a jour les deux feeds en un clic
- **Feed ACP OpenAI** : Generation du fichier CSV 77 colonnes conforme au protocole [Agentic Commerce Protocol](https://github.com/openai/acp)
- **Feed Google Merchant Center** : Mise a jour du fichier XLSX pour Google Shopping (38 colonnes)
- **Extraction GTIN** : Codes-barres EAN-13 extraits automatiquement depuis les fichiers Etiquettes
- **Apercu & Stats** : Tableaux interactifs, taux de remplissage, graphiques de disponibilite et distribution des prix

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
streamlit run app.py
```

L’application démarre sur `http://localhost:8501`.

### Organisation des dossiers et fichiers

```
ACP/
│
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/           # Config Streamlit (optionnel)
│
├── Files/                # Données sources (import/export)
│   ├── Intégration ACP - Feuille 1.csv
│   ├── Etiquette-AB - final.csv
│   ├── Etiquette-CD - final.csv
│   ├── export-variants-2026-03-12.xlsx
│   └── ...
│
├── Files to update/      # Fichiers générés/exportés automatiquement
│   ├── ACP_OpenAI_Feed.csv
│   └── Flux Google Merchant Center – Products source.xlsx
│
├── Scripts/              # Scripts utilitaires
│   ├── convert_to_acp.py
│   ├── generate_pdf.py
│   ├── gen_pdf.py
│   └── related_products.json
│
├── Design/               # Documentation, maquettes, visuels
│   ├── code.html
│   └── screen.png
└── ...
```

#### Fichiers requis (à placer dans les bons dossiers)

| Dossier / Fichier | Description |
|-------------------|-------------|
| `Files/Intégration ACP - Feuille 1.csv` | Export Google Shopping (source initiale) |
| `Files/export-variants-2026-03-12.xlsx` | Export ERP (fichier à importer) |
| `Files/Etiquette-AB - final.csv` | Codes-barres groupe A-B |
| `Files/Etiquette-CD - final.csv` | Codes-barres groupe C-D |
| `Scripts/related_products.json` | Groupes de produits associés |

#### Fichiers générés automatiquement

| Dossier / Fichier | Description |
|-------------------|-------------|
| `Files to update/ACP_OpenAI_Feed.csv` | Feed ACP OpenAI (77 colonnes) |
| `Files to update/Flux Google Merchant Center – Products source (1).xlsx` | Feed Google Merchant Center |

### Navigation

L’interface propose deux pages via la sidebar :

1. **Importer le fichier Export ERP** : Import du fichier ERP, génération automatique des feeds, aperçu, téléchargement et sauvegarde locale dans `Files to update/`
2. **Aperçu des fichiers actuels** : Consultation des feeds ACP et GMC existants, statistiques, téléchargement

## Installation & Prérequis

1. **Python 3.12+** installé (recommandé : venv ou conda)
2. Installer les dépendances :
	```bash
	pip install -r requirements.txt
	```
3. Placer tous les fichiers requis dans les bons dossiers (voir plus haut)
4. (Optionnel) Configurer le dossier `.streamlit/` pour personnaliser l’UI

## Stack technique

- **Python 3.12+**
- **Streamlit 1.50+** — Interface web
- **Pandas** — Traitement des données
- **openpyxl** — Lecture/écriture Excel

## Design System

L'interface utilise la charte graphique Calebasse :
- Vert principal : `#89B832`
- Fond : `#F9F9F7`
- Typographie : Georgia (titres), Manrope (corps)
