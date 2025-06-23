#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script final pour nettoyer Firebase AVANT de lancer l'application corrigée.
Ce script va supprimer toutes les collections problématiques.
"""

import sys
import os
import logging
import time

# Ajouter le répertoire parent au chemin de recherche
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services nécessaires
from app.services.firebase_service import FirebaseService

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_firebase():
    """
    Nettoyage radical des collections problématiques
    """
    firebase_service = FirebaseService()
    
    # Liste des collections problématiques
    collections = [
        "module_indexes_modules",
        "module_indexes_modules_application_principale",
        "module_indexes_modules_dev_application_principale_v2",
        "module_indexes_modules_dev_application_principale",
        "module_indexes_modules_application_principale_v2"
    ]
    
    for collection in collections:
        logger.info(f"Nettoyage de la collection: {collection}")
        try:
            # Récupérer tous les documents de la collection
            docs = firebase_service.get_collection(collection)
            if not docs:
                logger.info(f"Collection vide ou inexistante: {collection}")
                continue
                
            # Supprimer chaque document
            for doc in docs:
                # Afficher tous les détails du document pour debugger
                logger.info(f"Détails du document: {doc}")
                
                # Récupérer l'ID
                doc_id = doc.get('id')
                if doc_id:
                    # Vérifier si c'est lié à application_principale
                    if "application_principale" in str(doc).lower():
                        logger.info(f"Suppression du document lié à l'application principale: {collection}/{doc_id}")
                        firebase_service.delete_document(collection, doc_id)
                        # Attendre un peu pour s'assurer de la suppression
                        time.sleep(0.2)
                        
            logger.info(f"Collection {collection} nettoyée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de la collection {collection}: {str(e)}")
    
    logger.info("Nettoyage complet terminé!")

if __name__ == "__main__":
    logger.info("=== NETTOYAGE FINAL DES COLLECTIONS FIREBASE ===")
    clean_firebase()
    logger.info("=== NETTOYAGE TERMINÉ - VOUS POUVEZ MAINTENANT LANCER L'APPLICATION ===")
