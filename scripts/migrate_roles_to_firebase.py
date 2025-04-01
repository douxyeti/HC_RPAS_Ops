from pathlib import Path
import sys
import os
import json
import time

# Ajoute le répertoire parent au PYTHONPATH pour pouvoir importer les modules de l'application
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from app.services.config_service import ConfigService
from app.services.firebase_service import FirebaseService

def backup_config():
    """Crée une sauvegarde du fichier config.json"""
    try:
        config_path = Path(parent_dir) / 'data' / 'config' / 'config.json'
        backup_path = config_path.parent / f'config_backup_{int(time.time())}.json'
        
        with open(config_path, 'r', encoding='utf-8') as source:
            with open(backup_path, 'w', encoding='utf-8') as target:
                json.dump(json.load(source), target, indent=4, ensure_ascii=False)
        
        print(f"Sauvegarde créée : {backup_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {str(e)}")
        return False

def migrate_roles():
    """Migre les rôles vers Firebase"""
    print("\nDébut de la migration des rôles vers Firebase...")
    
    # Initialise les services
    config_service = ConfigService()
    firebase_service = FirebaseService.get_instance()
    
    try:
        # Récupère les rôles depuis config.json
        roles_config = config_service.get_config("interface.roles", {})
        if not roles_config:
            print("Aucun rôle trouvé dans config.json")
            return False
            
        print(f"\nNombre de rôles trouvés : {len(roles_config)}")
        print("Rôles à migrer :")
        for role_id, role_data in roles_config.items():
            print(f"- {role_data.get('name', role_id)}")
        
        # Crée une sauvegarde avant la migration
        if not backup_config():
            print("Erreur lors de la sauvegarde, migration annulée")
            return False
        
        # Migre les rôles vers Firebase
        print("\nMigration des rôles vers Firebase...")
        success = firebase_service.migrate_roles_from_config(roles_config)
        if not success:
            print("Erreur lors de la migration vers Firebase")
            return False
            
        # Vérifie que la migration s'est bien passée
        print("\nVérification de la migration...")
        firebase_roles = firebase_service.get_roles_and_tasks()
        if not firebase_roles:
            print("Erreur : Impossible de vérifier les rôles dans Firebase")
            return False
            
        if len(firebase_roles) != len(roles_config):
            print(f"Attention : Nombre de rôles différent entre config.json ({len(roles_config)}) et Firebase ({len(firebase_roles)})")
            return False
            
        print("\nMigration réussie !")
        print(f"Nombre total de rôles migrés : {len(firebase_roles)}")
        return True
        
    except Exception as e:
        print(f"\nErreur lors de la migration : {str(e)}")
        return False

if __name__ == "__main__":
    print("\nDémarrage de la migration des rôles vers Firebase...")
    print("Une sauvegarde de config.json sera créée automatiquement.")
    
    success = migrate_roles()
    if not success:
        print("\nLa migration a échoué")
        sys.exit(1)
    
    print("\nMigration terminée avec succès")
    sys.exit(0)
