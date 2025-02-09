from kivymd.app import MDApp
from kivy.lang import Builder
from .views.screens.scroll_screen import ScrollScreen
from pathlib import Path

class ScrollTestApp(MDApp):
    """Application principale de test de défilement"""
    
    def build(self):
        """Construction de l'application"""
        self.theme_cls.theme_style = "Light"
        
        # Charger le fichier KV
        kv_path = Path(__file__).parent / "views" / "kv" / "scroll_screen.kv"
        Builder.load_file(str(kv_path))
        
        return ScrollScreen()
