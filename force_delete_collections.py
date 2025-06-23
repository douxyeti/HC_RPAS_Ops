#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour supprimer directement les collections problématiques
"""

import sys
import os
import logging

# Ajouter le répertoire parent au chemin de recherche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services nécessaires
from app.services.firebase_service import FirebaseService

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Supprime directement les collections problématiques
    """
    # Initialiser le service Firebase
    firebase_service = FirebaseService()
    
    # Liste des collections problématiques à supprimer totalement
    collections_to_delete = [
        "module_indexes_modules",  # Collection générique
        "module_indexes_modules_application_principale",  # Application principale sans préfixe
        "module_indexes_modules_dev_application_principale",  # Dev application principale
        "module_indexes_modules_dev_application_principale_v2"  # Dev application principale v2
    ]
    
    # Boucle sur chaque collection pour la supprimer
    for collection_name in collections_to_delete:
        logger.info(f"Tentative de suppression de la collection: {collection_name}")
        try:
            # Récupérer d'abord tous les documents
            docs = firebase_service.get_collection(collection_name)
            if not docs:
                logger.info(f"Collection vide ou inexistante: {collection_name}")
                continue
            
            # Supprimer chaque document
            for doc in docs:
                doc_id = doc.get('id', None)
                if doc_id:
                    firebase_service.delete_document(collection_name, doc_id)
                    logger.info(f"Document supprimé: {collection_name}/{doc_id}")
            
            logger.info(f"Collection {collection_name} nettoyée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la collection {collection_name}: {str(e)}")

if __name__ == "__main__":
    logger.info("=== DÉBUT DU NETTOYAGE FORCÉ DES COLLECTIONS PROBLÉMATIQUES ===")
    main()
    logger.info("=== NETTOYAGE TERMINÉ ===")
