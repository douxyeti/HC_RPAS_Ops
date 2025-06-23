#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour supprimer TOUTES les collections de modules d'application principale
"""

import sys
import os
import logging

# Ajouter le répertoire parent au chemin de recherche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services nécessaires
from app.services.firebase_service import FirebaseService
from app.utils.module_discovery import ModuleDiscovery

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Supprime toutes les collections liées à l'application principale
    """
    # Initialiser les services
    firebase_service = FirebaseService()
    discovery = ModuleDiscovery()
    
    # Liste des branches connues
    branches = discovery._get_known_branches()
    logger.info(f"Branches connues: {branches}")
    
    # Liste des collections à supprimer (tous les modules d'application principale)
    collections_to_clean = []
    for branch in branches:
        if branch:
            sanitized_branch = discovery._sanitize_branch_name(branch)
            collection_name = f"module_indexes_modules_{sanitized_branch}"
            
            # Récupérer les modules de cette collection
            modules = firebase_service.get_collection(collection_name)
            
            if modules:
                for module in modules:
                    module_id = module.get('id', '')
                    # Si ce module est lié à l'application principale, le marquer pour suppression
                    if 'application_principale' in module_id or 'application_principale' in module.get('branch', ''):
                        logger.info(f"Module d'application principale trouvé: {module_id} dans {collection_name}")
                        
                        # Supprimer le module
                        try:
                            firebase_service.delete_document(collection_name, module_id)
                            logger.info(f"Suppression du module: {collection_name}/{module_id}")
                        except Exception as e:
                            logger.error(f"Erreur lors de la suppression du module: {str(e)}")
    
    logger.info("Nettoyage terminé!")

if __name__ == "__main__":
    logger.info("=== DÉBUT DU NETTOYAGE COMPLET DES MODULES D'APPLICATION PRINCIPALE ===")
    main()
    logger.info("=== NETTOYAGE TERMINÉ ===")
