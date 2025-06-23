#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour nettoyer les collections Firebase qui causent des doublons
"""

import logging
import sys
import os

# Ajouter le répertoire parent au chemin de recherche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer le service Firebase
from app.services.firebase_service import FirebaseService

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_firebase_collections():
    """
    Supprime les collections génériques qui causent des doublons.
    Notamment 'module_indexes_modules' et 'module_indexes_modules_application_principale'
    """
    firebase_service = FirebaseService()
    
    # Liste des collections à supprimer
    collections_to_delete = [
        "module_indexes_modules",                      # Collection générique
        "module_indexes_modules_application_principale" # Collection de l'application principale sans préfixe dev_
    ]
    
    logger.info(f"Nettoyage des collections Firebase qui causent des doublons: {collections_to_delete}")
    
    for collection_name in collections_to_delete:
        try:
            # Récupérer tous les documents dans la collection
            docs = firebase_service.get_collection(collection_name)
            if not docs:
                logger.info(f"Collection vide ou inexistante: {collection_name}")
                continue
                
            # Supprimer chaque document dans la collection
            for doc in docs:
                doc_id = doc.get('id', None)
                if doc_id:
                    firebase_service.delete_document(collection_name, doc_id)
                    logger.info(f"Document supprimé: {collection_name}/{doc_id}")
                else:
                    logger.warning(f"Document sans ID trouvé dans {collection_name}")
            
            logger.info(f"Collection nettoyée: {collection_name}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de la collection {collection_name}: {str(e)}")

if __name__ == "__main__":
    logger.info("Début du nettoyage des collections Firebase...")
    cleanup_firebase_collections()
    logger.info("Nettoyage des collections Firebase terminé.")
