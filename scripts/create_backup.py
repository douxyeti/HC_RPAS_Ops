import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.services.backup_service import BackupService

def main():
    print("Création d'une nouvelle sauvegarde...")
    backup_service = BackupService()
    backup_path = backup_service.create_backup()
    
    if backup_path:
        print(f"Sauvegarde créée avec succès dans: {backup_path}")
    else:
        print("Erreur lors de la création de la sauvegarde")

if __name__ == "__main__":
    main()
