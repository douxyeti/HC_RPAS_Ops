import unittest
from unittest.mock import MagicMock, patch
import time
from pathlib import Path
from app.services.scheduler_service import SchedulerService
from app.services.backup_service import BackupService

class TestSchedulerService(unittest.TestCase):
    def setUp(self):
        self.scheduler = SchedulerService()
        self.backup_service = MagicMock(spec=BackupService)
        
    def tearDown(self):
        self.scheduler.stop()
        
    def test_scheduler_start_stop(self):
        """Test le démarrage et l'arrêt du planificateur"""
        self.scheduler.start(self.backup_service)
        self.assertTrue(self.scheduler._scheduler_thread.is_alive())
        
        self.scheduler.stop()
        self.assertFalse(self.scheduler._scheduler_thread.is_alive())
        
    def test_backup_scheduling(self):
        """Test la planification des sauvegardes"""
        with patch('schedule.every') as mock_schedule:
            self.scheduler.start(self.backup_service)
            time.sleep(2)  # Attendre que le thread démarre
            
            # Vérifie que le planificateur est actif
            self.assertTrue(self.scheduler._scheduler_thread.is_alive())
            
            # Vérifie que le service de backup est correctement passé
            self.assertEqual(self.scheduler._backup_service, self.backup_service)
        
    def test_backup_execution(self):
        """Test l'exécution d'une sauvegarde planifiée"""
        self.backup_service.create_backup.return_value = "/path/to/backup"
        
        # Exécute directement une sauvegarde
        self.scheduler._run_backup(self.backup_service)
        
        # Vérifie que la sauvegarde a été créée
        self.backup_service.create_backup.assert_called_once()
        # Vérifie que la rotation a été effectuée
        self.backup_service.rotate_backups.assert_called_once_with(max_backups=5)

if __name__ == '__main__':
    unittest.main()
