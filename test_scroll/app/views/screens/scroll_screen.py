from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from ...controllers.card_controller import CardController
from kivy.properties import StringProperty

class CardWidget(MDCard):
    """Widget de carte personnalisé"""
    title = StringProperty("")
    description = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ScrollScreen(MDScreen):
    """Écran principal avec défilement"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._controller = CardController()
        # Initialiser les cartes directement dans __init__
        self._initialize_cards()
        
    def _initialize_cards(self):
        """Initialise les cartes de test"""
        self._controller.initialize_test_data()
        self._display_cards()
        
    def _display_cards(self):
        """Affiche les cartes dans l'interface"""
        container = self.ids.card_container
        container.clear_widgets()
        
        for card_data in self._controller.get_all_cards():
            card = self._create_card_widget(card_data)
            container.add_widget(card)
            
    def _create_card_widget(self, card_data: dict):
        """Crée un widget de carte à partir des données"""
        return CardWidget(
            title=card_data["title"],
            description=card_data["description"],
            size_hint_y=None,
            height="100dp",
            md_bg_color=[0.9, 0.9, 1, 1],  # Bleu très clair, presque blanc
            radius=[8],
            padding="8dp"
        )
