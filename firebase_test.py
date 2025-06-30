#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour valider l'accès à Firebase
"""

import os
import sys
import time
import json
import traceback
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

def load_firebase_config():
    """Charge la configuration Firebase depuis le fichier .env"""
    print("[TEST] Chargement de la configuration .env...")
    load_dotenv()
    
    try:
        # Essayer de charger depuis le fichier app/config/config.json comme le fait l'application
        print("[TEST] Tentative de chargement du fichier de configuration...")
        config_path = os.path.join("app", "config", "config.json")
        if not os.path.exists(config_path):
            config_path = "config.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'firebase' in config:
                    print(f"[TEST] Configuration Firebase trouvée dans {config_path}")
                    return config['firebase']
    except Exception as e:
        print(f"[ERREUR] Problème lors du chargement de la configuration: {e}")
    
    # Si échec, essayer de construire manuellement la config
    print("[TEST] Tentative de construction manuelle de la configuration...")
    config = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID'),
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL', '')
    }
    
    # Vérifier si toutes les clés nécessaires sont présentes
    required_keys = ['apiKey', 'authDomain', 'projectId', 'storageBucket']
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        print(f"[ERREUR] Configuration Firebase incomplète. Clés manquantes: {missing_keys}")
        return None
    
    print("[TEST] Configuration Firebase construite à partir des variables d'environnement")
    return config

def initialize_firebase(config):
    """Initialise Firebase avec la configuration fournie"""
    try:
        print("[TEST] Initialisation de Firebase...")
        
        # Vérifier si des applications Firebase sont déjà initialisées
        if firebase_admin._apps:
            print("[TEST] Applications Firebase déjà initialisées.")
            for app in firebase_admin._apps:
                print(f"[TEST] Application Firebase: {app}")
            return True
        
        # Essayer avec les credentials par défaut
        print("[TEST] Tentative avec credentials.ApplicationDefault()...")
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': config['projectId'],
                'storageBucket': config['storageBucket']
            })
            print("[TEST] Firebase initialisé avec succès via ApplicationDefault")
            return True
        except Exception as e:
            print(f"[ERREUR] Échec de l'initialisation via ApplicationDefault: {e}")
            print(traceback.format_exc())
        
        # Si échec, essayer de trouver le fichier de clé service
        print("[TEST] Recherche d'un fichier de clé service...")
        service_account_paths = [
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            "firebase-service-account.json",
            "service-account.json",
            os.path.join("app", "config", "firebase-service-account.json"),
            os.path.join("app", "firebase-service-account.json")
        ]
        
        for path in service_account_paths:
            if path and os.path.exists(path):
                print(f"[TEST] Clé de service trouvée: {path}")
                try:
                    cred = credentials.Certificate(path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': config['projectId'],
                        'storageBucket': config['storageBucket']
                    })
                    print("[TEST] Firebase initialisé avec succès via fichier de clé service")
                    return True
                except Exception as e:
                    print(f"[ERREUR] Échec de l'initialisation avec la clé {path}: {e}")
        
        print("[ERREUR] Aucune méthode d'authentification Firebase n'a réussi")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur globale lors de l'initialisation de Firebase: {e}")
        print(traceback.format_exc())
        return False

def test_firestore_access():
    """Teste l'accès à Firestore"""
    try:
        print("\n[TEST] Test d'accès à Firestore...")
        db = firestore.client()
        
        # Test d'accès à différentes collections
        collections_to_test = ['roles', 'users', 'tasks', 'app_screens_index_application_principale']
        
        for collection_name in collections_to_test:
            print(f"\n[TEST] Tentative d'accès à la collection '{collection_name}'...")
            
            start_time = time.time()
            try:
                docs = db.collection(collection_name).limit(5).get(timeout=10)
                doc_count = len(list(docs))
                elapsed_time = time.time() - start_time
                
                print(f"[SUCCÈS] Accès à la collection '{collection_name}': {doc_count} documents récupérés en {elapsed_time:.2f} secondes")
                
                # Afficher les premiers documents pour vérifier leur contenu
                if doc_count > 0:
                    print(f"[INFO] Premier document de '{collection_name}':")
                    first_doc = docs[0].to_dict()
                    print(json.dumps(first_doc, indent=2, default=str)[:500] + "..." if len(json.dumps(first_doc)) > 500 else "")
            except Exception as e:
                elapsed_time = time.time() - start_time
                print(f"[ERREUR] Échec d'accès à '{collection_name}' après {elapsed_time:.2f} secondes: {e}")
                print(traceback.format_exc())
        
        print("\n[TEST] Tests d'accès à Firestore terminés")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur globale lors du test d'accès à Firestore: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Fonction principale du script de test"""
    print("=" * 80)
    print("SCRIPT DE TEST D'ACCÈS À FIREBASE")
    print("=" * 80)
    
    # 1. Charger la configuration
    config = load_firebase_config()
    if not config:
        print("[CRITIQUE] Impossible de charger la configuration Firebase. Test annulé.")
        return False
    
    # Afficher les informations de configuration (sans les clés sensibles)
    safe_config = {k: v if k not in ['apiKey', 'appId'] else '***MASKED***' for k, v in config.items()}
    print("\n[INFO] Configuration Firebase:")
    print(json.dumps(safe_config, indent=2))
    
    # 2. Initialiser Firebase
    if not initialize_firebase(config):
        print("[CRITIQUE] Échec de l'initialisation de Firebase. Test annulé.")
        return False
    
    # 3. Tester l'accès à Firestore
    test_firestore_access()
    
    print("\n" + "=" * 80)
    print("TEST D'ACCÈS À FIREBASE TERMINÉ")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
