from app.services.backup_service import BackupService
import logging

logging.basicConfig(level=logging.INFO)

def test_restore():
    backup_service = BackupService()
    # Restaure la dernière sauvegarde
    result = backup_service.restore_backup("backup_20250202_230159")
    if result:
        print("Restauration reussie!")
    else:
        print("Echec de la restauration")

if __name__ == "__main__":
    test_restore()
