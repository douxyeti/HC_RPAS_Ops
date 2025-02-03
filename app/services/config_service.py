import json
import os
from pathlib import Path

class ConfigService:
    def __init__(self):
        """Initialise le service de configuration"""
        self.config_path = Path("data/config/config.json")
        self.config = self._load_config()
        
    def _load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Le fichier de configuration n'existe pas : {self.config_path}")
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {str(e)}")
            raise
            
    def get_version(self):
        """Retourne la version de l'application"""
        return self.config.get('version', '1.0.0')
        
    def get_active_modules(self):
        """Retourne la liste des modules actifs"""
        return self.config.get('modules', {}).get('active_modules', [])
        
    def get_role_permissions(self, role):
        """Retourne les permissions pour un rôle donné"""
        roles = self.config.get('interface', {}).get('roles', {})
        return roles.get(role, {}).get('permissions', [])
        
    def get_ui_config(self):
        """Retourne la configuration de l'interface utilisateur"""
        return self.config.get('interface', {}).get('ui', {})
