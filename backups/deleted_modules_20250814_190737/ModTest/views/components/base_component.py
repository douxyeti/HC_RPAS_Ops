"""Composant de base pour tous les composants de tableau de bord"""

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.clock import Clock
from typing import Any, Dict, Optional, Callable

class BaseComponent(MDCard):
    """Composant de base avec une structure commune pour tous les composants"""
    
    def __init__(
        self,
        title: str,
        icon: str = "information",
        refresh_interval: Optional[int] = None,
        show_refresh: bool = True,
        show_settings: bool = True,
        on_refresh: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Configuration de base de la carte
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = dp(200)  # Hauteur par défaut
        self.elevation = 2
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = [0.95, 0.95, 0.95, 1]
        
        # Stockage des callbacks
        self._on_refresh = on_refresh
        self._on_settings = on_settings
        
        # En-tête avec titre et icônes
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=10,
            padding=[0, 0, 5, 0]
        )
        
        # Icône principale
        self.icon_button = MDIconButton(
            icon=icon,
            pos_hint={"center_y": 0.5}
        )
        
        # Titre
        self.title_label = MDLabel(
            text=title,
            bold=True,
            font_size="16sp",
            size_hint_x=0.7,
            valign="center"
        )
        
        # Conteneur pour les boutons d'action
        action_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.3,
            spacing=5,
            pos_hint={"center_y": 0.5}
        )
        
        # Bouton de rafraîchissement
        if show_refresh:
            self.refresh_button = MDIconButton(
                icon="refresh",
                pos_hint={"center_y": 0.5},
                on_release=self._handle_refresh
            )
            action_box.add_widget(self.refresh_button)
        
        # Bouton de paramètres
        if show_settings:
            self.settings_button = MDIconButton(
                icon="cog",
                pos_hint={"center_y": 0.5},
                on_release=self._handle_settings
            )
            action_box.add_widget(self.settings_button)
        
        # Assemblage de l'en-tête
        header.add_widget(self.icon_button)
        header.add_widget(self.title_label)
        header.add_widget(action_box)
        
        # Conteneur pour le contenu
        self.content = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            padding=[5, 5]
        )
        
        # Assemblage final
        self.add_widget(header)
        self.add_widget(self.content)
        
        # Configuration du rafraîchissement automatique
        if refresh_interval:
            Clock.schedule_interval(self._auto_refresh, refresh_interval)
    
    def _handle_refresh(self, *args):
        """Gère le clic sur le bouton de rafraîchissement"""
        if self._on_refresh:
            self._on_refresh()
    
    def _handle_settings(self, *args):
        """Gère le clic sur le bouton de paramètres"""
        if self._on_settings:
            self._on_settings()
    
    def _auto_refresh(self, dt):
        """Rafraîchit automatiquement le composant"""
        self._handle_refresh()
    
    def update_content(self, data: Any):
        """Met à jour le contenu du composant
        
        Args:
            data: Nouvelles données à afficher
        """
        raise NotImplementedError("La méthode update_content doit être implémentée par les classes filles")
    
    def set_loading(self, loading: bool = True):
        """Active ou désactive l'état de chargement
        
        Args:
            loading: True pour afficher le chargement, False pour le cacher
        """
        if loading:
            self.content.clear_widgets()
            loading_label = MDLabel(
                text="Chargement...",
                halign="center",
                valign="center"
            )
            self.content.add_widget(loading_label)
    
    def show_error(self, message: str):
        """Affiche un message d'erreur
        
        Args:
            message: Message d'erreur à afficher
        """
        self.content.clear_widgets()
        error_label = MDLabel(
            text=message,
            halign="center",
            valign="center",
            theme_text_color="Error"
        )
        self.content.add_widget(error_label)
