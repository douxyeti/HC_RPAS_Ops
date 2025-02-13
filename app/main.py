from kivymd.app import MDApp
from app.core.container import Container
from app.core.config import load_config

class MainApp(MDApp):
    """Application principale."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Charger la configuration
        config = load_config()
        
        # Initialiser le container
        self.container = Container()
        self.container.config.from_dict(config)
        
        # Créer les services
        self.firebase_service = self.container.firebase_service()
        self.task_manager = self.container.task_manager()
        self.dashboard_controller = self.container.dashboard_controller()
        
    def build(self):
        """Construit l'interface utilisateur principale."""
        # Créer l'écran principal
        dashboard_screen = self.container.specialized_dashboard()
        return dashboard_screen

if __name__ == '__main__':
    MainApp().run()
