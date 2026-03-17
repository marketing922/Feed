# Guide utilisateur de l’interface
##  Installation

### Prérequis
- Python 3.12 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes
**Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## 1. Accès à l’application
- Lancez la commande dans le terminal à la racine du projet.
```bash
streamlit run app.py
```

- L’interface s’ouvre automatiquement dans votre navigateur à l’adresse `http://localhost:8501`.

## 2. Navigation dans l’interface

### Barre latérale (Sidebar)
- **Importer le fichier Export ERP**
  - Cliquez sur ce menu pour accéder à la page d’import.
  - Sélectionnez le fichier `export-variants-YYYY-MM-DD.xlsx` à importer.
  - Cliquez sur le bouton d’import : les feeds ACP et GMC sont générés automatiquement.
  - Un aperçu des données importées, des statistiques et des options de téléchargement s’affichent.
- **Aperçu des fichiers actuels**
  - Consultez les feeds déjà générés (ACP et GMC).
  - Visualisez les statistiques : taux de remplissage, distribution des prix, disponibilité, etc.
  - Téléchargez les fichiers générés.

## 3. Fonctionnalités principales
- **Import ERP** : Met à jour les deux feeds à partir d’un export ERP.
- **Extraction automatique des codes-barres** depuis les fichiers d’étiquettes.
- **Normalisation des prix** et enrichissement des variantes produits.
- **Q&A et avertissements** intégrés dans le feed ACP.
- **Statistiques interactives** sur les données produits.

## 4. Conseils d’utilisation
- Placez tous les fichiers sources dans les bons dossiers avant d’importer.
- Si un fichier requis est manquant, un message d’erreur s’affichera.
- Les fichiers générés sont automatiquement sauvegardés dans `Files to update/`.
- Vous pouvez télécharger les feeds générés directement depuis l’interface.

## 5. FAQ rapide
- **Je ne vois pas mes fichiers ?**
  - Vérifiez qu’ils sont bien placés dans les dossiers attendus (`Files/`, `Files to update/`).
- **Erreur lors de l’import ?**
  - Vérifiez le format du fichier ERP et la présence des colonnes attendues.
- **Comment personnaliser l’interface ?**
  - Modifiez le dossier `.streamlit/` pour changer l’apparence (optionnel).
