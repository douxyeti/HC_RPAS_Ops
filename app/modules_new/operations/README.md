# Module de Contrôle Opérationnel des Vols

Ce module fait partie de la suite HighCloud RPAS Operations Manager et peut être utilisé de deux façons :

1. **En mode autonome** : Comme une application indépendante
2. **En mode intégré** : Comme un module importé dans l'application principale

## Structure du module

```
services/
  └── module_controle_vols/
      ├── __init__.py           # Point d'entrée pour l'import
      ├── main.py               # Pour exécution autonome
      ├── manifest.json         # Définition des écrans et champs
      ├── module_registry.py    # Système d'indexation des écrans
      ├── index_storage.py      # Stockage Firebase des index
      └── README.md             # Documentation du module
```

## Utilisation en mode autonome

Pour lancer le module comme une application indépendante :

```bash
python -m services.module_controle_vols.main
```

## Utilisation en mode intégré

Dans l'application principale, vous pouvez importer et utiliser le module comme suit :

```python
# Importer le module
import services.module_controle_vols as module_controle_vols

# Initialiser le module avec le service Firebase
firebase_service = app_container.firebase_service()
module_controle_vols.initialize(firebase_service)

# Obtenir le registre du module
registry = module_controle_vols.get_registry()

# Naviguer vers un écran spécifique
registry.navigate_to_screen("pilot_dashboard", app=app_instance)
```

## Indexation des écrans

Le module expose ses écrans et champs via un système d'indexation basé sur Firebase. Cela permet à l'application principale de :

1. Découvrir dynamiquement les écrans disponibles dans le module
2. Naviguer directement vers un écran/champ spécifique
3. Partager des données entre l'application principale et le module

## Firebase et synchronisation multi-utilisateurs

Les index sont stockés dans Firebase, ce qui permet :

- La synchronisation des écrans entre plusieurs utilisateurs
- L'accès aux mêmes écrans/champs depuis différents appareils
- La mise à jour dynamique des index sans redémarrage de l'application

## Développement du module

Pour ajouter un nouvel écran au module :

1. Créer l'écran dans `app/views/screens/`
2. Ajouter l'entrée correspondante dans `manifest.json`
3. Le nouvel écran sera automatiquement indexé et disponible
