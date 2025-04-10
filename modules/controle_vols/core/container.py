class Container:
    """Container pour l'injection de dépendances."""
    
    def __init__(self):
        self._services = {}
        self._config = {}
        
    def register_service(self, name: str, service: object) -> None:
        """Enregistre un service dans le container."""
        self._services[name] = service
        
    def get_service(self, name: str) -> object:
        """Récupère un service du container."""
        return self._services.get(name)
        
    def register_config(self, name: str, config: dict) -> None:
        """Enregistre une configuration dans le container."""
        self._config[name] = config
        
    def get_config(self, name: str) -> dict:
        """Récupère une configuration du container."""
        return self._config.get(name)
