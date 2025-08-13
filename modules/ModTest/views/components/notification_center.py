"""Composant d'affichage des notifications"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from .base_component import BaseComponent

# Définition des couleurs
STATUS_COLORS = {
    "green": "#4CAF50",
    "red": "#F44336",
    "yellow": "#FFEB3B",
    "blue": "#2196F3"
}

class NotificationCenter(BaseComponent):
    """Composant d'affichage des notifications"""

    def __init__(self, **kwargs):
        """Initialisation du composant"""
        super().__init__(
            title="Centre de Notifications",
            icon="bell",
            refresh_interval=30,  # Rafraîchir toutes les 30 secondes
            show_refresh=True,
            show_settings=True,
            **kwargs
        )

        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = dp(10)
        self.padding = dp(10)

        # Données initiales
        self.update_content({
            "notifications": [
                {
                    "title": "Bienvenue",
                    "message": "Bienvenue dans le centre de notifications",
                    "icon": "information",
                    "color": "blue",
                    "timestamp": "10:00"
                }
            ]
        })

    def update_content(self, data):
        """Mise à jour du contenu du composant"""
        self.content.clear_widgets()

        if not data["notifications"]:
            no_notif = MDLabel(
                text="Aucune notification",
                halign="center",
                theme_text_color="Secondary"
            )
            self.content.add_widget(no_notif)
            return

        # Créer une carte pour chaque notification
        for notif in data["notifications"]:
            notif_card = self._create_notification_card(notif)
            self.content.add_widget(notif_card)

    def _create_notification_card(self, notification):
        """Création d'une carte de notification"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(100),
            padding=dp(10),
            spacing=dp(5),
            elevation=2,
            radius=[10]
        )

        # En-tête avec titre et horodatage
        header = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10)
        )

        # Convertir la couleur hex en tuple RGBA
        color = get_color_from_hex(STATUS_COLORS[notification["color"]])

        icon = MDIconButton(
            icon=notification["icon"],
            theme_icon_color="Custom",
            icon_color=color,
            size_hint=(None, None),
            size=(dp(48), dp(48))
        )
        header.add_widget(icon)

        title_box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(2)
        )

        title = MDLabel(
            text=notification["title"],
            font_size="16sp",
            bold=True,
            theme_text_color="Custom",
            text_color=color
        )
        title_box.add_widget(title)

        timestamp = MDLabel(
            text=notification["timestamp"],
            font_size="12sp",
            theme_text_color="Secondary"
        )
        title_box.add_widget(timestamp)

        header.add_widget(title_box)
        card.add_widget(header)

        # Message
        message = MDLabel(
            text=notification["message"],
            font_size="14sp"
        )
        card.add_widget(message)

        return card
