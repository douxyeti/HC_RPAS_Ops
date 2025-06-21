#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer l'application principale comme module dans l'écosystème
et utiliser son index d'écrans dans la carte d'indexation.
"""

import os
import sys
import time
import datetime

# Ajouter le répertoire parent au path pour pouvoir importer les modules de l'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services nécessaires de l'application
from app.services.firebase_service import FirebaseService

# Nom de la branche et des collections
BRANCH_NAME = "dev_application_principale_v2"
MODULE_COLLECTION = f"module_indexes_modules_{BRANCH_NAME}"
SCREENS_INDEX_COLLECTION = f"app_screens_index_{BRANCH_NAME}"

def create_module_entry():
    """Créer une entrée pour l'application principale en tant que module"""
    firebase_service = FirebaseService()
    
    # Vérifier que l'index des écrans existe
    screens = firebase_service.get_collection(SCREENS_INDEX_COLLECTION)
    if not screens:
        print(f"Erreur: La collection d'index des écrans '{SCREENS_INDEX_COLLECTION}' est vide ou n'existe pas.")
        return False
    
    # Compter les écrans réels (exclure les métadonnées)
    real_screens = [s for s in screens if s.get('id') != 'app_screens_index']
    screen_count = len(real_screens)
    
    # Créer le module pour l'application principale
    module_data = {
        "id": "application_principale",
        "name": "Application Principale",
        "description": "Application centrale du HC RPAS Operations",
        "version": "1.0.1",  # Version de l'application
        "main_screen": "dashboard",  # Écran principal de l'application
        "updated_at": int(time.time()),
        "branch": BRANCH_NAME,
        "icon": "home-variant",  # Icône Material Design
        "type": "core",
        "category": "system",
        "screens_count": screen_count,
        "is_main_app": True  # Marquer comme application principale
    }
    
    # Ajouter dans la collection standard des modules (sans suffixe de branche)
    # pour que l'application principale soit toujours visible
    firebase_service.set_data("module_indexes_modules", module_data)
    print(f"Application principale créée comme module dans la collection 'module_indexes_modules'")
    
    # Ajouter aussi dans la collection spécifique à la branche
    firebase_service.set_data(MODULE_COLLECTION, module_data)
    print(f"Application principale créée comme module dans la collection '{MODULE_COLLECTION}'")
    
    # Idée: Pour chaque écran de l'index, créer une entrée dans la collection des écrans du module
    screens_collection = f"module_indexes_screens_application_principale_{BRANCH_NAME}"
    
    # D'abord, créer une entrée pour l'écran principal (dashboard)
    dashboard_data = {
        "id": "dashboard",
        "name": "Tableau de bord principal",
        "title": "Tableau de bord",
        "description": "Tableau de bord principal de l'application HC RPAS Operations",
        "module_id": "application_principale",
        "branch": BRANCH_NAME,
        "is_main": True
    }
    
    firebase_service.set_data(screens_collection, dashboard_data)
    print(f"Ajout de l'écran principal dans la collection '{screens_collection}'")
    
    # Ensuite, ajouter tous les écrans de l'application depuis l'index
    added_count = 0
    for i, screen in enumerate(real_screens):
        if 'id' not in screen:
            continue
            
        # Convertir les données du format d'index au format de module
        screen_data = {
            "id": screen['id'],
            "name": screen.get('name', screen['id']),
            "title": screen.get('title', screen.get('name', screen['id'])),
            "description": screen.get('description', f"Écran {screen.get('name', screen['id'])} de l'application principale"),
            "module_id": "application_principale",
            "branch": BRANCH_NAME,
            "file_path": screen.get('file_path', ''),
            "full_class_name": screen.get('full_class_name', ''),
            "added_from_index": True  # Marquer comme ajouté depuis l'index
        }
        
        # Ajouter l'écran à la collection des écrans du module
        firebase_service.set_data(screens_collection, screen_data)
        added_count += 1
        
        if i % 10 == 0:  # Log tous les 10 écrans
            print(f"Ajout de l'écran {screen.get('name', screen['id'])} ({added_count}/{len(real_screens)})")
    
    print(f"{added_count} écrans ajoutés à la collection '{screens_collection}'")
    return True

if __name__ == "__main__":
    print(f"Création du module d'index des écrans pour la branche {BRANCH_NAME}...")
    if create_module_entry():
        print("Opération terminée avec succès!")
    else:
        print("Échec de l'opération.")
