import sys
import os
from pathlib import Path
import schedule
import time
import logging
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.services.backup_service import BackupService

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / "scheduled_backup.log",
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("ScheduledBackup")

def perform_backup():
    logger = setup_logging()
    backup_service = BackupService()
    
    try:
        logger.info("Démarrage de la sauvegarde programmée")
        
        # Créer la sauvegarde
        backup_path = backup_service.create_backup()
        if backup_path:
            logger.info(f"Sauvegarde créée avec succès: {backup_path}")
        else:
            logger.error("Échec de la création de la sauvegarde")
            
        # Rotation des sauvegardes
        backup_service.rotate_backups(max_backups=5)
        logger.info("Rotation des sauvegardes terminée")
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde programmée: {str(e)}")

def main():
    logger = setup_logging()
    logger.info("Démarrage du service de sauvegarde programmée")
    
    # Programmer les sauvegardes
    schedule.every().day.at("23:00").do(perform_backup)  # Sauvegarde quotidienne à 23h
    schedule.every().sunday.at("02:00").do(perform_backup)  # Sauvegarde supplémentaire le dimanche
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Arrêt du service de sauvegarde programmée")
    except Exception as e:
        logger.error(f"Erreur dans le service de sauvegarde programmée: {str(e)}")

if __name__ == "__main__":
    main()
