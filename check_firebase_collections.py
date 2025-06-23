#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour vérifier les collections Firebase liées aux branches Git
"""

import os
import sys
import subprocess
import logging

# Ajouter le répertoire parent au path pour importer les modules de l'app
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importer les services nécessaires
try:
    from app.services.firebase_service import FirebaseService
    from app.modules_new.operations.index_storage import FirebaseIndexStorage
except ImportError as e:
    print(f"Impossible d'importer les modules nécessaires: {e}")
    sys.exit(1)

def main():
    """Fonction principale qui vérifie les collections dans Firebase"""
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialiser le service Firebase
        firebase_service = FirebaseService()
        logging.info("Service Firebase initialisé")
        
        # Initialiser le stockage d'index
        index_storage = FirebaseIndexStorage(firebase_service)
        branch_name = index_storage.branch_name
        
        # Afficher la branche Git détectée
        logging.info(f"Branche Git détectée: '{branch_name}'")
        
        # Vérifier les collections de modules standards et spécifiques à la branche
        standard_modules_collection = "module_indexes_modules"
        branch_modules_collection = f"module_indexes_modules_{branch_name}" if branch_name else ""
        
        # Vérifier la collection standard
        logging.info("=== Collections de modules standards ===")
        try:
            modules = firebase_service.get_collection(standard_modules_collection)
            logging.info(f"- {standard_modules_collection}: {len(modules)} document(s)")
            for doc in modules:
                if 'id' in doc:
                    logging.info(f"  * Module: {doc['id']} - {doc.get('name', 'Sans nom')}")
        except Exception as e:
            logging.warning(f"Impossible d'accéder à la collection {standard_modules_collection}: {e}")
        
        # Vérifier la collection spécifique à la branche
        if branch_name:
            logging.info(f"=== Collections de modules pour la branche '{branch_name}' ===")
            try:
                branch_modules = firebase_service.get_collection(branch_modules_collection)
                if branch_modules:
                    logging.info(f"- {branch_modules_collection}: {len(branch_modules)} document(s)")
                    for doc in branch_modules:
                        if 'id' in doc:
                            logging.info(f"  * Module: {doc['id']} - {doc.get('name', 'Sans nom')}")
                else:
                    logging.info(f"- {branch_modules_collection}: Collection vide ou inexistante")
            except Exception as e:
                logging.warning(f"Impossible d'accéder à la collection {branch_modules_collection}: {e}")
        
        # Pour chaque module trouvé, vérifier les écrans
        # D'abord dans la collection standard
        all_modules = {}
        try:
            standard_modules = firebase_service.get_collection(standard_modules_collection)
            if standard_modules:
                for doc in standard_modules:
                    if 'id' in doc:
                        all_modules[doc['id']] = "standard"
        except Exception:
            pass
        
        # Puis dans la collection de branche si elle existe
        if branch_name:
            try:
                branch_modules = firebase_service.get_collection(branch_modules_collection)
                if branch_modules:
                    for doc in branch_modules:
                        if 'id' in doc:
                            all_modules[doc['id']] = branch_name
            except Exception:
                pass
        
        # Vérifier les écrans pour chaque module
        logging.info("=== Collections d'écrans ===")
        for module_id, source in all_modules.items():
            standard_screens_collection = f"module_indexes_screens_{module_id}"
            branch_screens_collection = f"module_indexes_screens_{module_id}_{branch_name}" if branch_name else ""
            
            # Collection standard d'écrans
            try:
                screens = firebase_service.get_collection(standard_screens_collection)
                if screens:
                    logging.info(f"- {standard_screens_collection}: {len(screens)} écran(s)")
                    for doc in screens[:5]:  # Limiter à 5 pour éviter trop de logs
                        if 'id' in doc:
                            logging.info(f"  * Écran: {doc['id']}")
                    if len(screens) > 5:
                        logging.info(f"  * ... et {len(screens) - 5} autres écrans")
            except Exception as e:
                logging.warning(f"Impossible d'accéder à la collection {standard_screens_collection}: {e}")
            
            # Collection de branche d'écrans
            if branch_name:
                try:
                    branch_screens = firebase_service.get_collection(branch_screens_collection)
                    if branch_screens:
                        logging.info(f"- {branch_screens_collection}: {len(branch_screens)} écran(s)")
                        for doc in branch_screens[:5]:  # Limiter à 5 pour éviter trop de logs
                            if 'id' in doc:
                                logging.info(f"  * Écran: {doc['id']}")
                        if len(branch_screens) > 5:
                            logging.info(f"  * ... et {len(branch_screens) - 5} autres écrans")
                    else:
                        logging.info(f"- {branch_screens_collection}: Collection vide ou inexistante")
                except Exception as e:
                    logging.warning(f"Impossible d'accéder à la collection {branch_screens_collection}: {e}")
        
        # Conclusion
        branch_specific_collections_exist = False
        
        # Vérifier si la collection de modules de branche existe
        if branch_name:
            try:
                branch_modules = firebase_service.get_collection(branch_modules_collection)
                if branch_modules:
                    branch_specific_collections_exist = True
            except Exception:
                pass
            
            # Vérifier si une collection d'écrans de branche existe
            for module_id in all_modules.keys():
                branch_screens_collection = f"module_indexes_screens_{module_id}_{branch_name}"
                try:
                    branch_screens = firebase_service.get_collection(branch_screens_collection)
                    if branch_screens:
                        branch_specific_collections_exist = True
                        break
                except Exception:
                    pass
        
        if branch_name and branch_specific_collections_exist:
            logging.info(f"\n✅ Des collections spécifiques à la branche '{branch_name}' ont été trouvées!")
        elif branch_name:
            logging.warning(f"\n⚠️ Aucune collection spécifique à la branche '{branch_name}' n'a été trouvée.")
        else:
            logging.warning("\n⚠️ Aucune branche Git détectée, impossible de vérifier les collections spécifiques.")
            
    except Exception as e:
        logging.error(f"Erreur lors de la vérification des collections: {e}")
        return False
        
    return True

if __name__ == "__main__":
    main()
