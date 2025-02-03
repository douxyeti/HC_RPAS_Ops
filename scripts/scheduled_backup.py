import sys
import os
from pathlib import Path
import schedule
import time
import logging
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from app.services.backup_service import BackupService

def setup_logging():
    """Configure le système de logs"""
    log_dir = root_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / "scheduled_backup.log",
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("ScheduledBackup")

def perform_backup():
    """Exécute une sauvegarde"""
    logger = setup_logging()
    backup_service = BackupService()
    
    try:
        logger.info("Démarrage de la sauvegarde programmée")
        print("Démarrage de la sauvegarde...")
        
        # Créer la sauvegarde
        backup_path = backup_service.create_backup()
        if backup_path:
            logger.info(f"Sauvegarde créée avec succès: {backup_path}")
            print(f"Sauvegarde créée avec succès dans: {backup_path}")
        else:
            logger.error("Échec de la création de la sauvegarde")
            print("Échec de la création de la sauvegarde")
            
        # Rotation des sauvegardes
        backup_service.rotate_backups(max_backups=5)
        logger.info("Rotation des sauvegardes terminée")
        print("Rotation des sauvegardes terminée")
        
    except Exception as e:
        error_msg = f"Erreur lors de la sauvegarde programmée: {str(e)}"
        logger.error(error_msg)
        print(f"ERREUR: {error_msg}")

def main():
    """Fonction principale"""
    logger = setup_logging()
    logger.info("Démarrage du service de sauvegarde programmée")
    print("\nService de sauvegarde automatique démarré")
    print("Les sauvegardes seront effectuées :")
    print("- Tous les jours à 23h00")
    print("- Le dimanche à 02h00")
    
    # Programmer les sauvegardes
    schedule.every().day.at("23:00").do(perform_backup)
    schedule.every().sunday.at("02:00").do(perform_backup)
    
    # Effectuer une première sauvegarde au démarrage
    print("\nExécution de la première sauvegarde...")
    perform_backup()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
            
    except KeyboardInterrupt:
        logger.info("Arrêt du service de sauvegarde programmée")
        print("\nArrêt du service de sauvegarde programmée")
    except Exception as e:
        error_msg = f"Erreur dans le service de sauvegarde programmée: {str(e)}"
        logger.error(error_msg)
        print(f"\nERREUR: {error_msg}")
        raise  # Relancer l'exception pour voir la trace complète

if __name__ == "__main__":
    main()
