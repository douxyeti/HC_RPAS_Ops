# HighCloud RPAS Operations Manager (Development Version)

Application de gestion des opérations de drones pour HighCloud RPAS. Cette version est en développement actif et peut contenir des fonctionnalités expérimentales.

## Fonctionnalités

- Interface moderne avec Material Design (KivyMD)
- Gestion des missions de drones
- Gestion du personnel et des qualifications
- Système d'authentification sécurisé avec Firebase
- Base de données en temps réel
- Transitions fluides entre les écrans
- Splash screen interactif

## Prérequis

- Python 3.9+
- Les dépendances listées dans `requirements.txt`

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/votre-repo/HC_RPAS_Ops.git
cd HC_RPAS_Ops
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
- Copier le fichier `.env.example` vers `.env`
- Remplir les variables d'environnement requises dans `.env`

## Lancement de l'application

Pour lancer l'application, exécutez simplement :
```bash
python main.py
```

## Structure du projet

```
HC_RPAS_Ops/
├── app/                    # Code source principal
│   ├── services/          # Services (Firebase, Config, etc.)
│   ├── views/             # Écrans et fichiers KV
│   └── utils/             # Utilitaires
├── assets/                # Ressources (images, fonts, etc.)
├── data/                  # Données locales
├── docs/                  # Documentation
├── modules/               # Modules additionnels
├── tests/                 # Tests unitaires
├── .env                   # Variables d'environnement
├── main.py               # Point d'entrée de l'application
└── requirements.txt      # Dépendances Python
```

## Tests

Pour exécuter les tests :
```bash
pytest tests/
```

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## License

Ce projet est sous licence propriétaire. Tous droits réservés.
