from app.services.backup_service import BackupService
from app.services.scheduler_service import SchedulerService
import time
import logging
from pathlib import Path
import argparse

def main():
    # Parse les arguments
    parser = argparse.ArgumentParser(description='Service de sauvegarde automatique')
    parser.add_argument('--test', action='store_true', help='Effectue une seule sauvegarde et quitte')
    args = parser.parse_args()

    # 1. Configuration des logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "backup.log")
        ]
    )
    
    # 2. Création des répertoires
    data_dir = Path("data")
    backup_dir = data_dir / "backups"
    config_dir = data_dir / "config"
    
    for d in [data_dir, backup_dir, config_dir]:
        d.mkdir(exist_ok=True)
        logging.info(f"Répertoire créé/vérifié: {d}")
    
    # 3. Initialisation des services
    try:
        backup_service = BackupService()
        if not args.test:
            scheduler = SchedulerService()
        logging.info("Services initialisés avec succès")
    except Exception as e:
        logging.error(f"Erreur d'initialisation des services: {e}")
        return
    
    # 4. Sauvegarde
    try:
        backup_path = backup_service.create_backup()
        if backup_path:
            logging.info(f"Sauvegarde créée: {backup_path}")
        else:
            logging.error("Échec de la sauvegarde")
            return
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde: {e}")
        return
    
    # Si mode test, on s'arrête ici
    if args.test:
        logging.info("Test terminé avec succès")
        return
        
    # 5. Démarrage du planificateur
    try:
        scheduler.start(backup_service)
        logging.info("Planificateur démarré")
        logging.info("Configuration des sauvegardes :")
        logging.info("- Tous les jours à 3h du matin")
        logging.info("- Toutes les 6 heures")
        logging.info("Les 5 sauvegardes les plus récentes seront conservées")
        logging.info("\nAppuyez sur Ctrl+C pour arrêter...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("\nArrêt demandé...")
        scheduler.stop()
        logging.info("Service arrêté")
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        scheduler.stop()

if __name__ == "__main__":
    main()
