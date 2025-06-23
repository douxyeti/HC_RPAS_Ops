#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour lister toutes les collections Firebase et leur contenu
"""

import sys
import os
import logging

# Ajouter le répertoire parent au chemin de recherche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer le service Firebase
from app.services.firebase_service import FirebaseService

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def list_all_collections():
    """
    Liste toutes les collections Firebase et leur contenu
    """
    firebase_service = FirebaseService()
    
    # Récupérer toutes les collections
    try:
        collections = firebase_service.get_collections()
        logger.info(f"Collections trouvées: {len(collections)}")
        
        # Filtrer pour n'afficher que les collections liées aux modules
        module_collections = [c for c in collections if c.startswith('module_indexes_')]
        logger.info(f"Collections de modules trouvées: {len(module_collections)}")
        
        # Afficher le contenu de chaque collection
        for collection_name in module_collections:
            logger.info(f"\n===== Collection: {collection_name} =====")
            
            # Récupérer tous les documents dans la collection
            docs = firebase_service.get_collection(collection_name)
            logger.info(f"Documents trouvés: {len(docs) if docs else 0}")
            
            if docs:
                for i, doc in enumerate(docs):
                    logger.info(f"--- Document {i+1} ---")
                    for key, value in doc.items():
                        if key in ['id', 'branch', 'name']:
                            logger.info(f"{key}: {value}")

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des collections: {str(e)}")

if __name__ == "__main__":
    logger.info("Listing de toutes les collections Firebase...")
    list_all_collections()
    logger.info("Listing terminé.")
