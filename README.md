# HighCloud RPAS Operations Manager v2.0

Application de gestion des opérations de drones (RPAS) pour HighCloud, conforme aux réglementations de Transports Canada.

## Structure de l'Application

L'application est organisée selon une architecture MVVM avec KivyMD 2.x et utilise une approche de synchronisation multi-niveaux :

- Interface utilisateur moderne avec KivyMD 2.x
- Stockage local SQLite pour les opérations hors-ligne
- Base de données centrale MySQL
- Services cloud Firebase pour la synchronisation et le backup

## Fonctionnalités Principales

1. Gestion des Documents
   - Manuel d'Exploitation (politiques)
   - Manuel des Documents Incorporés (procédures)
   - Système de renvois entre manuels

2. Modules Opérationnels
   - Contrôle des vols
   - Gestion du personnel et des qualifications
   - Maintenance des RPAS
   - Formation et certification

3. Synchronisation Multi-niveaux
   - Opérations hors-ligne garanties
   - Synchronisation automatique
   - Triple redondance des données

## Installation

1. Créer un environnement virtuel Python :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurer les variables d'environnement dans `.env`

4. Lancer l'application :
   ```bash
   python main.py
   ```

## Configuration

Créer un fichier `.env` à la racine du projet avec les configurations nécessaires :

```
DB_HOST=localhost
DB_USER=user
DB_PASSWORD=password
DB_NAME=highcloud_rpas

FIREBASE_CONFIG_PATH=path/to/firebase-config.json
```

## Structure du Projet

```
├── app/
│   ├── models/         # Modèles de données
│   ├── views/          # Écrans et widgets KivyMD
│   ├── viewmodels/     # ViewModels (MVVM)
│   ├── services/       # Services (DB, Firebase, etc.)
│   └── utils/          # Utilitaires
├── data/
│   ├── local/         # Base SQLite
│   └── config/        # Fichiers de configuration
├── docs/              # Documentation
├── resources/         # Ressources (images, etc.)
└── tests/            # Tests unitaires
```

## Licence

Propriétaire - HighCloud © 2025
