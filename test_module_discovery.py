#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier que la classe ModuleDiscovery utilise correctement
les collections Firebase spécifiques à la branche Git courante.
"""

import sys
import logging
import importlib.util
import os
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('test_module_discovery')

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
    logger.info("Démarrage du test de ModuleDiscovery avec les collections Firebase spécifiques à la branche")
    
    # Détecter la branche Git actuelle
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        logger.info(f"Branche Git détectée: {branch}")
    except Exception as e:
        logger.error(f"Erreur lors de la détection de la branche Git: {e}")
        branch = "inconnu"
    
    # Charger le module FirebaseService
    try:
        from firebase_admin import initialize_app, firestore
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
        logger.info("ModuleDiscovery initialisé")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de ModuleDiscovery: {e}")
        return
    
    # Afficher les informations sur les collections Firebase spécifiques à la branche
    logger.info("==== Collections Firebase attendues pour cette branche ====")
    modules_collection = f"module_indexes_modules_{branch}" if branch else "module_indexes_modules"
    logger.info(f"Collection modules: {modules_collection}")
    
    # Récupérer et afficher les modules depuis Firebase
    try:
        logger.info("==== Récupération des modules dans Firebase ====")
        modules = module_discovery.get_installed_modules()
        logger.info(f"Nombre de modules trouvés: {len(modules)}")
        
        for idx, module in enumerate(modules):
            module_id = module.get('id', 'N/A')
            module_name = module.get('name', 'N/A')
            module_branch = module.get('branch', 'N/A')
            logger.info(f"Module {idx+1}: ID={module_id}, Nom={module_name}, Branche={module_branch}")
            
            # Récupérer et afficher les écrans pour ce module
            screens_collection = f"module_indexes_screens_{module_id}_{branch}" if branch else f"module_indexes_screens_{module_id}"
            logger.info(f"  Collection écrans: {screens_collection}")
            
            screens = module_discovery.get_module_screens(module_id)
            logger.info(f"  Nombre d'écrans trouvés: {len(screens)}")
            
            for s_idx, screen in enumerate(screens):
                screen_id = screen.get('id', 'N/A')
                screen_name = screen.get('name', 'N/A')
                screen_branch = screen.get('branch', 'N/A')
                logger.info(f"  Écran {s_idx+1}: ID={screen_id}, Nom={screen_name}, Branche={screen_branch}")
        
        if not modules:
            logger.warning(f"ATTENTION: Aucun module trouvé dans la collection {modules_collection}")
            logger.info("Vérifiez que la branche Git est correcte et que les collections existent dans Firebase")
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modules et écrans: {e}")
    
    logger.info("Test terminé")

if __name__ == "__main__":
    main()
