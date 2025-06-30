#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier le chargement des variables d'environnement
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("=" * 80)
    print("TEST DE CHARGEMENT DES VARIABLES D'ENVIRONNEMENT")
    print("=" * 80)
    
    # Tester le chargement direct depuis .env
    print("\n1. Test de chargement avec dotenv.load_dotenv() :")
    result = load_dotenv()
    print(f"Résultat du chargement: {'Succès' if result else 'Échec'}")
    
    # Vérifier les variables Firebase essentielles
    firebase_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_API_KEY',
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_STORAGE_BUCKET',
    ]
    
    print("\n2. Vérification des variables Firebase essentielles :")
    for var in firebase_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:4] + '...' + value[-4:] if len(value) > 10 else '***'
            print(f"  [OK] {var} est défini ({masked_value})")
        else:
            print(f"  [NON] {var} n'est PAS défini")
    
    # Vérifier si d'autres méthodes sont utilisées pour charger les variables
    print("\n3. Vérification d'autres méthodes potentielles :")
    
    # Vérifier le chemin du fichier .env
    env_paths = [
        '.env',
        os.path.join('app', '.env'),
        os.path.join('app', 'config', '.env'),
    ]
    
    print("\n4. Recherche du fichier .env :")
    for path in env_paths:
        if os.path.exists(path):
            print(f"  [OK] Fichier .env trouvé à: {path}")
        else:
            print(f"  [NON] Pas de fichier .env à: {path}")
    
    # Vérifier la variable GOOGLE_APPLICATION_CREDENTIALS
    gac = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    print("\n5. Variable GOOGLE_APPLICATION_CREDENTIALS :")
    if gac:
        print(f"  [OK] Définie: {gac}")
        if os.path.exists(gac):
            print(f"  [OK] Le fichier existe")
        else:
            print(f"  [NON] Le fichier n'existe PAS")
    else:
        print("  [NON] Non définie")
    
    print("\n6. Chercher les fichiers de clés de service potentiels :")
    potential_key_files = [
        'firebase-service-account.json',
        'service-account.json',
        os.path.join('app', 'config', 'firebase-service-account.json'),
        os.path.join('app', 'firebase-service-account.json'),
    ]
    
    for path in potential_key_files:
        if os.path.exists(path):
            print(f"  [OK] Fichier de clé trouvé: {path}")
        else:
            print(f"  [NON] Pas de fichier de clé à: {path}")
    
    print("\n" + "=" * 80)
    print("TEST DE CHARGEMENT DES VARIABLES D'ENVIRONNEMENT TERMINÉ")
    print("=" * 80)

if __name__ == "__main__":
    main()
