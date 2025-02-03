import os
import json
import shutil
import sqlite3
from datetime import datetime
import logging
from pathlib import Path
from typing import Optional

class BackupService:
    """Service de gestion des sauvegardes"""
    
    def __init__(self):
        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure le système de logs"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / "backup.log",
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("BackupService")
        
    def create_backup(self) -> Optional[str]:
        """Crée une sauvegarde complète"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Sauvegarde de la base SQLite
            self._backup_sqlite(backup_path)
            
            # Sauvegarde des configurations
            self._backup_configs(backup_path)
            
            # Création du manifeste
            self._create_manifest(backup_path, timestamp)
            
            self.logger.info(f"Sauvegarde créée avec succès: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return None
            
    def _backup_sqlite(self, backup_path: Path):
        """Sauvegarde la base de données SQLite"""
        db_path = Path("data/database.db")
        if db_path.exists():
            shutil.copy2(db_path, backup_path / "database.db")
            
    def _backup_configs(self, backup_path: Path):
        """Sauvegarde les fichiers de configuration"""
        config_dir = Path("data/config")
        if config_dir.exists():
            shutil.copytree(config_dir, backup_path / "config")
            
    def _create_manifest(self, backup_path: Path, timestamp: str):
        """Crée un fichier manifeste pour la sauvegarde"""
        manifest = {
            "timestamp": timestamp,
            "version": "1.0.0",
            "files": [str(p.relative_to(backup_path)) for p in backup_path.rglob("*") if p.is_file()]
        }
        
        with open(backup_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=4)
            
    def restore_backup(self, backup_path: str) -> bool:
        """Restaure une sauvegarde"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                self.logger.error(f"Sauvegarde non trouvée: {backup_path}")
                return False
                
            # Vérification du manifeste
            manifest_path = backup_dir / "manifest.json"
            if not manifest_path.exists():
                self.logger.error("Manifeste de sauvegarde manquant")
                return False
                
            # Restauration de la base SQLite
            db_backup = backup_dir / "database.db"
            if db_backup.exists():
                shutil.copy2(db_backup, "data/database.db")
                
            # Restauration des configurations
            config_backup = backup_dir / "config"
            if config_backup.exists():
                shutil.rmtree("data/config", ignore_errors=True)
                shutil.copytree(config_backup, "data/config")
                
            self.logger.info(f"Sauvegarde restaurée avec succès depuis: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la restauration: {str(e)}")
            return False
            
    def rotate_backups(self, max_backups: int = 5):
        """Supprime les sauvegardes les plus anciennes"""
        try:
            backups = sorted(
                [d for d in self.backup_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime
            )
            
            while len(backups) > max_backups:
                oldest = backups.pop(0)
                shutil.rmtree(oldest)
                self.logger.info(f"Sauvegarde supprimée: {oldest}")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la rotation des sauvegardes: {str(e)}")
            
    def get_backup_list(self):
        """Retourne la liste des sauvegardes disponibles"""
        backups = []
        try:
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    manifest_path = backup_dir / "manifest.json"
                    if manifest_path.exists():
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                            backups.append({
                                "path": str(backup_dir),
                                "timestamp": manifest["timestamp"],
                                "version": manifest.get("version", "unknown")
                            })
            return backups
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture des sauvegardes: {str(e)}")
            return []
