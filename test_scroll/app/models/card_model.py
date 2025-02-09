from dataclasses import dataclass
from typing import List

@dataclass
class CardModel:
    """Modèle de données pour une carte"""
    title: str
    description: str
    
class CardCollection:
    """Gestionnaire de collection de cartes"""
    def __init__(self):
        self._cards: List[CardModel] = []
        
    def add_card(self, title: str, description: str) -> None:
        """Ajoute une nouvelle carte à la collection"""
        self._cards.append(CardModel(title=title, description=description))
        
    def get_cards(self) -> List[CardModel]:
        """Retourne la liste des cartes"""
        return self._cards.copy()
        
    def generate_test_cards(self, count: int = 20) -> None:
        """Génère des cartes de test"""
        for i in range(count):
            self.add_card(
                title=f"Carte {i+1}",
                description=f"Description de la carte {i+1}"
            )
