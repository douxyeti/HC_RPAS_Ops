from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

class AdminAssistantDashboardScreen(MDScreen):
    """Tableau de bord pour l'adjoint(e) administratif(ve)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # En-tête
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[10, 0]
        )
        
        title = MDLabel(
            text="Tableau de bord - Adjoint(e) administratif(ve)",
            font_style="Headline",
            size_hint_y=None,
            height=dp(50)
        )
        
        header.add_widget(title)
        
        # Grille pour les cartes
        self.grid = MDGridLayout(
            cols=2,
            spacing=dp(20),
            padding=dp(10),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # Ajouter les widgets au layout principal
        self.layout.add_widget(header)
        self.layout.add_widget(self.grid)
        self.add_widget(self.layout)
