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

# Nom des collections uniques
MODULE_COLLECTION = "module_indexes_modules"
SCREENS_INDEX_COLLECTION = "app_screens_index"

def create_module_entry():
    """Créer une entrée pour l'application principale en tant que module"""
    firebase_service = FirebaseService()
    
    # Vérifier que l'index des écrans existe
    all_screens = []
    max_retries = 3
    retry_delay = 5  # secondes

    for attempt in range(max_retries):
        print(f"Tentative {attempt + 1}/{max_retries} de récupération de l'index '{SCREENS_INDEX_COLLECTION}'...")
        all_screens = firebase_service.get_collection(SCREENS_INDEX_COLLECTION)
        
        # On filtre le document de métadonnées pour ne garder que les vrais écrans
        all_screens = [doc for doc in all_screens if doc.get('id') != 'app_screens_index']
        
        if all_screens:
            print(f"Index trouvé avec {len(all_screens)} documents d'écrans.")
            break
            
        if attempt < max_retries - 1:
            print(f"L'index est vide ou ne contient que des métadonnées. Prochaine tentative dans {retry_delay} secondes...")
            time.sleep(retry_delay)

    if not all_screens:
        print(f"ERREUR: La collection d'index '{SCREENS_INDEX_COLLECTION}' est restée vide après {max_retries} tentatives.")
        return False
    
    # Compter les écrans réels (exclure les métadonnées)
    screen_count = len(all_screens)
    
    # Créer le module pour l'application principale
    module_data = {
        "id": "application_principale",
        "name": "Application Principale",
        "description": "Application centrale du HC RPAS Operations",
        "version": "1.0.1",  # Version de l'application
        "main_screen": "dashboard",  # Écran principal de l'application
        "updated_at": int(time.time()),
        "icon": "home-variant",  # Icône Material Design
        "type": "core",
        "category": "system",
        "screens_count": screen_count,
        "is_main_app": True  # Marquer comme application principale
    }
    
    # Ajouter/Mettre à jour dans la collection standard des modules
    firebase_service.set_data(MODULE_COLLECTION, module_data)
    print(f"Application principale créée/mise à jour comme module dans la collection '{MODULE_COLLECTION}'")
    
    # Collection pour les écrans de ce module
    screens_collection_name = f"module_indexes_screens_application_principale"
    
    # D'abord, créer une entrée pour l'écran principal (dashboard)
    dashboard_data = {
        "id": "dashboard",
        "name": "Tableau de bord principal",
        "title": "Tableau de bord",
        "description": "Tableau de bord principal de l'application HC RPAS Operations",
        "module_id": "application_principale",
        "is_main": True
    }
    
    firebase_service.set_data(screens_collection_name, dashboard_data)
    print(f"Ajout de l'écran principal dans la collection '{screens_collection_name}'")
    
    # Ensuite, ajouter tous les écrans de l'application depuis l'index
    added_count = 0
    for i, screen in enumerate(all_screens):
        if 'id' not in screen:
            continue
            
        # Convertir les données du format d'index au format de module
        screen_data = {
            "id": screen['id'],
            "name": screen.get('name', screen['id']),
            "title": screen.get('title', screen.get('name', screen['id'])),
            "description": screen.get('description', f"Écran {screen.get('name', screen['id'])} de l'application principale"),
            "module_id": "application_principale",
            "file_path": screen.get('file_path', ''),
            "full_class_name": screen.get('full_class_name', ''),
            "added_from_index": True  # Marquer comme ajouté depuis l'index
        }
        
        # Ajouter l'écran à la collection des écrans du module
        firebase_service.set_data(screens_collection_name, screen_data)
        added_count += 1
        
        if i % 10 == 0:  # Log tous les 10 écrans
            print(f"Ajout de l'écran {screen.get('name', screen['id'])} ({added_count}/{len(all_screens)})")
    
    print(f"{added_count} écrans ajoutés à la collection '{screens_collection_name}'")
    return True

if __name__ == "__main__":
    print("Création du module d'index pour l'application principale...")
    if create_module_entry():
        print("Opération terminée avec succès!")
    else:
        print("Échec de l'opération.")
