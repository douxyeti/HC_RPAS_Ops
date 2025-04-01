import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
import re
from datetime import datetime
import random

def generate_role_id(name):
    """Génère un ID unique basé sur le nom du rôle"""
    # Convertit en minuscules et remplace les espaces par des underscores
    role_id = name.lower().strip()
    role_id = re.sub(r'[^a-z0-9]+', '_', role_id)
    # Ajoute un timestamp avec microsecondes et nombre aléatoire pour garantir l'unicité
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    random_suffix = str(random.randint(1000, 9999))
    return f"{role_id}_{timestamp}_{random_suffix}"

def migrate_roles():
    """Migre les rôles sans ID vers des rôles avec ID unique"""
    firebase_service = FirebaseService()
    roles = firebase_service.get_collection('roles')
    
    # Garde une trace des modifications pour le rapport
    migrations = []
    errors = []
    
    print("Début de la migration des rôles...")
    
    for role in roles:
        try:
            # Si le rôle n'a pas d'ID explicite
            if 'id' not in role:
                new_id = generate_role_id(role['name'])
                role_data = role.copy()
                role_data['id'] = new_id
                
                # Crée le nouveau document avec l'ID
                firebase_service.add_document_with_id('roles', new_id, role_data)
                migrations.append({
                    'name': role['name'],
                    'old_id': 'NO_ID',
                    'new_id': new_id
                })
                print(f"Migré: {role['name']} -> {new_id}")
        except Exception as e:
            errors.append({
                'role': role.get('name', 'Unknown'),
                'error': str(e)
            })
            print(f"Erreur lors de la migration de {role.get('name', 'Unknown')}: {str(e)}")
    
    # Génère un rapport de migration
    print("\nRapport de migration:")
    print(f"Total des rôles migrés: {len(migrations)}")
    print(f"Total des erreurs: {len(errors)}")
    
    if migrations:
        print("\nDétails des migrations:")
        for migration in migrations:
            print(f"- {migration['name']}: {migration['old_id']} -> {migration['new_id']}")
    
    if errors:
        print("\nErreurs rencontrées:")
        for error in errors:
            print(f"- {error['role']}: {error['error']}")

def cleanup_migrated_roles():
    """Supprime les rôles qui ont été migrés précédemment"""
    firebase_service = FirebaseService()
    roles = firebase_service.get_collection('roles')
    
    print("Nettoyage des rôles migrés précédemment...")
    deleted_count = 0
    
    for role in roles:
        # Si le rôle a un ID généré automatiquement (contient un timestamp)
        if 'id' in role and re.search(r'_\d{14}', role.get('id', '')):
            try:
                firebase_service.delete_document('roles', role['id'])
                deleted_count += 1
                print(f"Supprimé: {role['name']} (ID: {role['id']})")
            except Exception as e:
                print(f"Erreur lors de la suppression de {role.get('name', 'Unknown')}: {str(e)}")
    
    print(f"\nTotal des rôles nettoyés: {deleted_count}")

if __name__ == '__main__':
    cleanup_migrated_roles()
    migrate_roles()
