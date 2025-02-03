import unittest
from pathlib import Path
import shutil
import json
from app.services.backup_service import BackupService

class TestBackupService(unittest.TestCase):
    def setUp(self):
        self.backup_service = BackupService()
        self.test_data_dir = Path("test_data")
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Créer des données de test
        (self.test_data_dir / "database.db").touch()
        (self.test_data_dir / "config").mkdir(exist_ok=True)
        with open(self.test_data_dir / "config/test.json", "w") as f:
            json.dump({"test": "data"}, f)
            
    def tearDown(self):
        shutil.rmtree(self.test_data_dir)
        shutil.rmtree(self.backup_service.backup_dir, ignore_errors=True)
        
    def test_create_backup(self):
        """Test la création d'une sauvegarde"""
        backup_path = self.backup_service.create_backup()
        self.assertIsNotNone(backup_path)
        self.assertTrue(Path(backup_path).exists())
        self.assertTrue((Path(backup_path) / "manifest.json").exists())
        
    def test_restore_backup(self):
        """Test la restauration d'une sauvegarde"""
        # Créer une sauvegarde
        backup_path = self.backup_service.create_backup()
        
        # Supprimer les données originales
        shutil.rmtree("data/config", ignore_errors=True)
        Path("data/database.db").unlink(missing_ok=True)
        
        # Restaurer
        result = self.backup_service.restore_backup(backup_path)
        self.assertTrue(result)
        self.assertTrue(Path("data/config").exists())
        
    def test_rotate_backups(self):
        """Test la rotation des sauvegardes"""
        # Créer plusieurs sauvegardes
        for _ in range(7):
            self.backup_service.create_backup()
            
        # Rotation avec max_backups = 5
        self.backup_service.rotate_backups(max_backups=5)
        
        backups = list(self.backup_service.backup_dir.iterdir())
        self.assertEqual(len(backups), 5)
        
    def test_get_backup_list(self):
        """Test la récupération de la liste des sauvegardes"""
        # Créer quelques sauvegardes
        for _ in range(3):
            self.backup_service.create_backup()
            
        backup_list = self.backup_service.get_backup_list()
        self.assertEqual(len(backup_list), 3)
        for backup in backup_list:
            self.assertIn("timestamp", backup)
            self.assertIn("version", backup)
            self.assertIn("path", backup)

if __name__ == '__main__':
    unittest.main()
