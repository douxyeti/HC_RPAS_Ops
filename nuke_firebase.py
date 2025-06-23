#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour TOUT nettoyer dans Firebase - Méthode radicale
"""

import sys
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def nuke_firebase_collections():
    """
    SUPPRIME RADICALEMENT TOUTES les collections liées à 'application_principale'
    """
    # Récupérer la configuration Firebase depuis le fichier config
    import json
    
    try:
        # Initialiser Firebase avec le compte de service (nécessaire pour une suppression complète)
        cred = credentials.ApplicationDefault()
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        # Obtenir toutes les collections
        collections = db.collections()
        
        for collection in collections:
            collection_id = collection.id
            
            # Vérifier si c'est une collection de modules
            if collection_id.startswith('module_indexes_'):
                logger.info(f"Examen de la collection: {collection_id}")
                
                # Vérifier si c'est lié à application_principale
                if 'application_principale' in collection_id:
                    logger.info(f"SUPPRESSION DE LA COLLECTION COMPLÈTE: {collection_id}")
                    
                    # Supprimer tous les documents
                    docs = collection.stream()
                    for doc in docs:
                        logger.info(f"Suppression du document: {doc.id}")
                        doc.reference.delete()
                    
                    logger.info(f"Collection {collection_id} entièrement supprimée")
                else:
                    # Pour les autres collections, supprimer seulement les documents liés à application_principale
                    docs = collection.stream()
                    for doc in docs:
                        doc_data = doc.to_dict()
                        
                        # Vérifier si ce document est lié à application_principale
                        is_app_principale = False
                        for key, value in doc_data.items():
                            if isinstance(value, str) and 'application_principale' in value.lower():
                                is_app_principale = True
                                break
                        
                        if is_app_principale:
                            logger.info(f"Suppression du document lié à application_principale dans {collection_id}: {doc.id}")
                            doc.reference.delete()
        
        logger.info("NETTOYAGE COMPLET TERMINÉ")
        
    except Exception as e:
        logger.error(f"ERREUR CRITIQUE: {str(e)}")

if __name__ == "__main__":
    logger.info("=== DÉBUT DU NETTOYAGE RADICAL DES COLLECTIONS FIREBASE ===")
    nuke_firebase_collections()
    logger.info("=== NETTOYAGE TERMINÉ - VOUS POUVEZ MAINTENANT MODIFIER LE CODE SOURCE ===")
