"""
Écran principal du module de base
Cet écran sert de template pour les écrans principaux des nouveaux modules
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import logging

logger = logging.getLogger("hc_rpas.nom_nouveau_module.main_screen")

class MainScreen(MDScreen):
    """Écran principal du module de base"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        logger.info("Initialisation de l'écran principal du module de base")
        
        # Créer le layout principal
        self.layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16)
        )
        
        # Ajouter un titre
        self.title = MDLabel(
            text="Controle_vols - Écran Principal",
            theme_font_size="Custom",
            font_size="24sp",
            bold=True,
            size_hint_y=None,
            height=dp(36)
        )
        self.layout.add_widget(self.title)
        
        # Ajouter une description
        self.description = MDLabel(
            text="Ce module sert de template pour la création de nouveaux modules. "
                 "Modifiez ce contenu pour l'adapter à vos besoins spécifiques.",
            theme_font_size="Custom",
            font_size="16sp",
            size_hint_y=None,
            height=dp(60)
        )
        self.layout.add_widget(self.description)
        
        # Ajouter un conteneur pour les fonctionnalités
        self.features_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )
        
        # Exemple de fonctionnalité (bouton)
        self.button = MDButton(
            style="elevated",
            on_release=self.button_callback,
            size_hint=(None, None),
            size=(dp(200), dp(48)),
            pos_hint={"center_x": 0.5}
        )
        self.button.add_widget(MDButtonText(text="TESTER LE MODULE"))
        self.features_box.add_widget(self.button)
        
        # Ajouter le conteneur de fonctionnalités au layout principal
        self.layout.add_widget(self.features_box)
        
        # Spacer pour pousser le contenu vers le haut
        self.layout.add_widget(MDBoxLayout())
        
        # Ajouter le layout principal à l'écran
        self.add_widget(self.layout)
    
    def button_callback(self, instance):
        """Callback pour le bouton de test"""
        logger.info("Bouton de test pressé")
        
        # Mettre à jour la description pour montrer que le bouton fonctionne
        self.description.text = "Le bouton a été pressé! Ce module fonctionne correctement."
    
    def on_enter(self):
        """Appelé lorsque l'écran devient actif"""
        logger.info("Entrée dans l'écran principal du module de base")
    
    def on_leave(self):
        """Appelé lorsque l'écran devient inactif"""
        logger.info("Sortie de l'écran principal du module de base")
