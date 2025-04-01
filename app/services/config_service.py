import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

class ConfigService:
    """Service de gestion des configurations de l'application"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _replace_env_vars(self, config: Any) -> Any:
        """Remplace les variables d'environnement dans la configuration
        
        Args:
            config: Configuration à traiter (dict, list, str, ou autre type)
            
        Returns:
            Configuration avec les variables d'environnement remplacées
        """
        if isinstance(config, dict):
            return {key: self._replace_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            env_value = os.getenv(env_var)
            if env_value is None:
                print(f"Attention: Variable d'environnement non trouvée: {env_var}")
                return config
            return env_value
        return config
    
    def _initialize(self) -> None:
        """Initialise le service de configuration"""
        try:
            # Charge les variables d'environnement
            load_dotenv()
            
            # Charge la configuration JSON
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = base_dir / 'data' / 'config' / 'config.json'
            
            if not config_path.exists():
                print(f"Note: Fichier de configuration non trouvé: {config_path}")
                self._config = {}
            else:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Remplace les variables d'environnement
                    self._config = self._replace_env_vars(config)
                
            print("Configuration chargée avec succès")
            
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {str(e)}")
            raise

    def get_env(self, key: str, default: Any = None) -> Any:
        """Récupère une variable d'environnement
        
        Args:
            key: Clé de la variable
            default: Valeur par défaut si non trouvée
            
        Returns:
            La valeur de la variable ou la valeur par défaut
        """
        value = os.getenv(key, default)
        if value is None:
            print(f"Attention: Variable d'environnement non trouvée: {key}")
        return value

    def get_config(self, path: str = None, default: Any = None) -> Any:
        """Récupère une valeur de configuration par son chemin
        
        Args:
            path: Chemin de la configuration (ex: "interface.roles.admin"). Si None, retourne toute la configuration.
            default: Valeur par défaut si non trouvée
            
        Returns:
            La valeur de configuration ou la valeur par défaut
        """
        if path is None:
            return self._config
            
        try:
            value = self._config
            for key in path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_firebase_config(self) -> Dict[str, Any]:
        """Récupère la configuration Firebase complète
        
        Returns:
            Dict contenant toute la configuration Firebase
        """
        return self.get_config('firebase', {})

    def get_database_config(self) -> Dict[str, str]:
        """Récupère la configuration de la base de données
        
        Returns:
            Dict contenant la configuration de la base de données
        """
        return {
            'host': self.get_env('DB_HOST'),
            'user': self.get_env('DB_USER'),
            'password': self.get_env('DB_PASSWORD'),
            'database': self.get_env('DB_NAME')
        }

    def get_app_config(self) -> Dict[str, Any]:
        """Récupère la configuration générale de l'application
        
        Returns:
            Dict contenant la configuration de l'application
        """
        return {
            'name': self.get_env('APP_NAME', 'HighCloud RPAS'),
            'version': self.get_env('APP_VERSION', '2.0.0'),
            'debug': self.get_env('DEBUG_MODE', 'False').lower() == 'true',
            'sync_interval': int(self.get_env('SYNC_INTERVAL', '300')),
            'max_retry_attempts': int(self.get_env('MAX_RETRY_ATTEMPTS', '3')),
            'offline_cache_size': int(self.get_env('OFFLINE_CACHE_SIZE', '1000'))
        }

    def get_module_config(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Récupère la configuration d'un module spécifique
        
        Args:
            module_name: Nom du module
            
        Returns:
            Dict contenant la configuration du module ou None si non trouvé
        """
        return self.get_config(f"modules.{module_name}")

    def is_module_active(self, module_name: str) -> bool:
        """Vérifie si un module est actif
        
        Args:
            module_name: Nom du module à vérifier
            
        Returns:
            True si le module est actif, False sinon
        """
        active_modules = self.get_config("modules.active_modules", [])
        return module_name in active_modules

    def get_module_dependencies(self, module_name: str) -> list:
        """Récupère les dépendances d'un module
        
        Args:
            module_name: Nom du module
            
        Returns:
            Liste des dépendances du module
        """
        return self.get_config(f"modules.dependencies.{module_name}", [])

    def get_roles_and_tasks(self) -> Dict[str, Any]:
        """Récupère les rôles et tâches, prioritairement depuis Firebase
        
        Returns:
            Dict contenant les rôles et leurs tâches
        """
        from .firebase_service import FirebaseService
        
        # Essaie d'abord de récupérer depuis Firebase
        firebase_roles = FirebaseService.get_instance().get_roles_and_tasks()
        if firebase_roles is not None:
            return firebase_roles
            
        # Fallback sur config.json si Firebase échoue
        return self.get_config("interface.roles", {})

    def migrate_roles_to_firebase(self) -> bool:
        """Migre les rôles et tâches vers Firebase
        
        Returns:
            True si la migration a réussi, False sinon
        """
        from .firebase_service import FirebaseService
        
        roles_config = self.get_config("interface.roles", {})
        return FirebaseService.get_instance().migrate_roles_from_config(roles_config)
