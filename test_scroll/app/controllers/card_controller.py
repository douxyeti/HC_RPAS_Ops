from ..models.card_model import CardCollection
from typing import List

class CardController:
    """Contrôleur pour la gestion des cartes"""
    def __init__(self):
        self._card_collection = CardCollection()
        
    def initialize_test_data(self, count: int = 20) -> None:
        """Initialise les données de test"""
        self._card_collection.generate_test_cards(count)
        
    def get_all_cards(self) -> List[dict]:
        """Retourne toutes les cartes formatées pour l'affichage"""
        cards = self._card_collection.get_cards()
        return [{"title": card.title, "description": card.description} for card in cards]
