"""Composant d'affichage du statut des opérations"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
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

class OperationsStatus(BaseComponent):
    """Composant d'affichage du statut des opérations"""

    def __init__(self, **kwargs):
        """Initialisation du composant"""
        super().__init__(
            title="État des Opérations",
            icon="airplane",
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
            "flight_status": "En cours",
            "flight_color": "green",
            "flight_icon": "airplane",
            "battery_status": "85%",
            "battery_color": "green",
            "battery_icon": "battery-80",
            "signal_status": "Fort",
            "signal_color": "green",
            "signal_icon": "signal",
            "weather_status": "Favorable",
            "weather_color": "green",
            "weather_icon": "weather-sunny"
        })

    def update_content(self, data):
        """Mise à jour du contenu du composant"""
        self.content.clear_widgets()

        # Statuts
        flight_box = self._create_status_line(
            data["flight_icon"],
            data["flight_color"],
            "Vol",
            data["flight_status"]
        )
        self.content.add_widget(flight_box)

        battery_box = self._create_status_line(
            data["battery_icon"],
            data["battery_color"],
            "Batterie",
            data["battery_status"]
        )
        self.content.add_widget(battery_box)

        signal_box = self._create_status_line(
            data["signal_icon"],
            data["signal_color"],
            "Signal",
            data["signal_status"]
        )
        self.content.add_widget(signal_box)

        weather_box = self._create_status_line(
            data["weather_icon"],
            data["weather_color"],
            "Météo",
            data["weather_status"]
        )
        self.content.add_widget(weather_box)

    def _create_status_line(self, icon_name, icon_color, label_text, status_text):
        """Création d'une ligne de statut"""
        box = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10)
        )

        # Convertir la couleur hex en tuple RGBA
        color = get_color_from_hex(STATUS_COLORS[icon_color])

        icon = MDIconButton(
            icon=icon_name,
            theme_icon_color="Custom",
            icon_color=color,
            size_hint=(None, None),
            size=(dp(48), dp(48))
        )
        box.add_widget(icon)

        label = MDLabel(
            text=label_text,
            font_size="16sp",
            size_hint_x=None,
            width=dp(100),
            theme_text_color="Custom",
            text_color=color
        )
        box.add_widget(label)

        status = MDLabel(
            text=status_text,
            font_size="16sp",
            theme_text_color="Custom",
            text_color=color
        )
        box.add_widget(status)

        return box
