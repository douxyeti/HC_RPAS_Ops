#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier que la classe ModuleDiscovery récupère correctement
les modules et écrans de toutes les branches qui ont des modules dans Firebase.
"""

import sys
import logging
import importlib.util
import os
from pathlib import Path
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('test_all_branch_modules')

def import_module_from_file(module_name, file_path):
    """Importe un module à partir d'un fichier"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Erreur lors de l'importation du module {module_name} depuis {file_path}: {e}")
        return None

def main():
    """Fonction principale"""
    logger.info("===== TEST DE RÉCUPÉRATION DES MODULES DE TOUTES LES BRANCHES =====")
    
    # Charger le module FirebaseService
    try:
        firebase_module_path = Path("app") / "services" / "firebase_service.py"
        
        if not firebase_module_path.exists():
            logger.error(f"Le fichier {firebase_module_path} n'existe pas")
            return
        
        firebase_module = import_module_from_file("firebase_service", firebase_module_path)
        if not firebase_module:
            return
        
        FirebaseService = firebase_module.FirebaseService
        firebase_service = FirebaseService()
        logger.info("Service Firebase initialisé")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service Firebase: {e}")
        return
    
    # Charger le module ModuleDiscovery
    try:
        module_discovery_path = Path("app") / "utils" / "module_discovery.py"
        
        if not module_discovery_path.exists():
            logger.error(f"Le fichier {module_discovery_path} n'existe pas")
            return
        
        module_discovery_module = import_module_from_file("module_discovery", module_discovery_path)
        if not module_discovery_module:
            return
        
        ModuleDiscovery = module_discovery_module.ModuleDiscovery
        module_discovery = ModuleDiscovery(firebase_service)
        logger.info(f"ModuleDiscovery initialisé pour la branche: {module_discovery.branch_name}")
        
        # Tenter d'implémenter la méthode get_collections sur FirebaseService si elle n'existe pas
        if not hasattr(firebase_service, 'get_collections'):
            logger.warning("La méthode get_collections n'est pas disponible dans FirebaseService")
            logger.info("Tentative d'ajout dynamique de la méthode...")
            
            def get_collections_mock(self):
                """Méthode temporaire pour récupérer les collections Firebase"""
                try:
                    # Utiliser la méthode client pour lister les collections
                    if hasattr(self, 'firestore_client') and self.firestore_client:
                        collections = self.firestore_client.collections()
                        return [col.id for col in collections]
                    else:
                        logger.error("Impossible d'accéder au client Firestore")
                        return []
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des collections: {e}")
                    return []
            
            # Ajouter la méthode temporairement à l'instance FirebaseService
            import types
            firebase_service.get_collections = types.MethodType(get_collections_mock, firebase_service)
            logger.info("Méthode get_collections ajoutée temporairement")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de ModuleDiscovery: {e}")
        return
    
    # Récupérer et afficher les modules depuis toutes les branches
    try:
        logger.info("\n===== MODULES DE TOUTES LES BRANCHES =====")
        modules = module_discovery.get_installed_modules()
        logger.info(f"Nombre total de modules trouvés dans toutes les branches: {len(modules)}")
        
        # Organiser les modules par branche pour une meilleure lisibilité
        modules_by_branch = {}
        for module in modules:
            branch = module.get('branch', 'inconnu')
            if branch not in modules_by_branch:
                modules_by_branch[branch] = []
            modules_by_branch[branch].append(module)
        
        # Afficher les modules par branche
        for branch, branch_modules in modules_by_branch.items():
            logger.info(f"\n----- Branche: {branch} ({len(branch_modules)} modules) -----")
            for idx, module in enumerate(branch_modules):
                module_id = module.get('id', 'N/A')
                module_name = module.get('name', 'N/A')
                logger.info(f"Module {idx+1}: ID={module_id}, Nom={module_name}")
                
                # Récupérer et afficher les écrans pour ce module
                screens = module_discovery.get_module_screens(module_id)
                
                # Organiser les écrans par branche
                screens_by_branch = {}
                for screen in screens:
                    screen_branch = screen.get('branch', 'inconnu')
                    if screen_branch not in screens_by_branch:
                        screens_by_branch[screen_branch] = []
                    screens_by_branch[screen_branch].append(screen)
                
                logger.info(f"  Nombre total d'écrans pour {module_id}: {len(screens)}")
                
                # Afficher les écrans par branche
                for screen_branch, branch_screens in screens_by_branch.items():
                    logger.info(f"  - Écrans de la branche {screen_branch}: {len(branch_screens)}")
                    for s_idx, screen in enumerate(branch_screens[:3]):  # Limiter à 3 écrans par branche pour la lisibilité
                        screen_id = screen.get('id', 'N/A')
                        screen_name = screen.get('name', 'N/A')
                        logger.info(f"    Écran {s_idx+1}: ID={screen_id}, Nom={screen_name}")
                    
                    if len(branch_screens) > 3:
                        logger.info(f"    ... et {len(branch_screens) - 3} autres écrans")
        
        # Enregistrer les résultats dans un fichier JSON pour référence
        with open('all_branch_modules.json', 'w', encoding='utf-8') as f:
            json.dump({
                'modules_count': len(modules),
                'branches_count': len(modules_by_branch),
                'modules_by_branch': {k: [{'id': m.get('id'), 'name': m.get('name')} for m in v] 
                                     for k, v in modules_by_branch.items()}
            }, f, ensure_ascii=False, indent=4)
        logger.info("\nRésultats enregistrés dans all_branch_modules.json")
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modules et écrans: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n===== TEST TERMINÉ =====")

if __name__ == "__main__":
    main()
