import schedule
import time
import threading
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

class SchedulerService:
    """Service de planification des tâches automatiques"""
    
    def __init__(self):
        self.setup_logging()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._backup_service = None
        
    def setup_logging(self):
        """Configure le système de logs"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / "scheduler.log",
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("SchedulerService")
    
    def start(self, backup_service):
        """Démarre le planificateur en arrière-plan"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self.logger.warning("Le planificateur est déjà en cours d'exécution")
            return
            
        self._stop_flag.clear()
        self._backup_service = backup_service
        
        # Planifie une sauvegarde quotidienne à 3h du matin
        schedule.every().day.at("03:00").do(self._run_backup, backup_service)
        
        # Planifie une sauvegarde toutes les 6 heures
        schedule.every(6).hours.do(self._run_backup, backup_service)
        
        self._scheduler_thread = threading.Thread(target=self._run_scheduler)
        self._scheduler_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
        self._scheduler_thread.start()
        
        self.logger.info("Planificateur démarré")
        
    def stop(self):
        """Arrête le planificateur"""
        if not self._scheduler_thread or not self._scheduler_thread.is_alive():
            return
            
        self._stop_flag.set()
        self._scheduler_thread.join()
        schedule.clear()
        self.logger.info("Planificateur arrêté")
        
    def _run_scheduler(self):
        """Boucle principale du planificateur"""
        while not self._stop_flag.is_set():
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les minutes
            
    def _run_backup(self, backup_service):
        """Exécute une sauvegarde et gère les erreurs"""
        try:
            self.logger.info("Démarrage de la sauvegarde planifiée")
            backup_path = backup_service.create_backup()
            
            if backup_path:
                self.logger.info(f"Sauvegarde planifiée réussie: {backup_path}")
                # Rotation des sauvegardes pour garder les 5 plus récentes
                backup_service.rotate_backups(max_backups=5)
            else:
                self.logger.error("Échec de la sauvegarde planifiée")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde planifiée: {str(e)}")
