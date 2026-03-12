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

L'application demarre sur `http://localhost:8501`.

### Fichiers requis dans le repertoire

| Fichier | Description |
|---------|-------------|
| `Flux Google Merchant Center – Products source.xlsx` | Feed GMC existant (base de donnees produits) |
| `Etiquette-AB - final.csv` | Codes-barres groupe A-B |
| `Etiquette-CD - final.csv` | Codes-barres groupe C-D |
| `related_products.json` | Groupes de produits associes |

### Navigation

L'interface propose deux pages via la sidebar :

1. **Importer le fichier Export ERP** : Upload, generation, resultats, apercu des donnees generees, telechargement et sauvegarde locale
2. **Apercu des fichiers actuels** : Consultation des fichiers ACP et GMC existants avec statistiques

## Stack technique

- **Python 3.12+**
- **Streamlit 1.50+** — Interface web
- **Pandas** — Traitement des donnees
- **openpyxl** — Lecture/ecriture Excel

## Design System

L'interface utilise la charte graphique Calebasse :
- Vert principal : `#89B832`
- Fond : `#F9F9F7`
- Typographie : Georgia (titres), Manrope (corps)
