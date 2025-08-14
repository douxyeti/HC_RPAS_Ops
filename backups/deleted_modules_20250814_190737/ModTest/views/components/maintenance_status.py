"""Composant d'affichage du statut de maintenance"""

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

class MaintenanceStatus(BaseComponent):
    """Composant d'affichage du statut de maintenance"""

    def __init__(self, **kwargs):
        """Initialisation du composant"""
        super().__init__(
            title="État de la Maintenance",
            icon="wrench",
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
            "scheduled_status": "2 prévues",
            "scheduled_color": "blue",
            "scheduled_icon": "calendar-check",
            "ongoing_status": "1 en cours",
            "ongoing_color": "green",
            "ongoing_icon": "wrench",
            "overdue_status": "Aucune",
            "overdue_color": "green",
            "overdue_icon": "alert",
            "parts_status": "Stock OK",
            "parts_color": "green",
            "parts_icon": "package-variant"
        })

    def update_content(self, data):
        """Mise à jour du contenu du composant"""
        self.content.clear_widgets()

        # Statuts
        scheduled_box = self._create_status_line(
            data["scheduled_icon"],
            data["scheduled_color"],
            "Planifiées",
            data["scheduled_status"]
        )
        self.content.add_widget(scheduled_box)

        ongoing_box = self._create_status_line(
            data["ongoing_icon"],
            data["ongoing_color"],
            "En cours",
            data["ongoing_status"]
        )
        self.content.add_widget(ongoing_box)

        overdue_box = self._create_status_line(
            data["overdue_icon"],
            data["overdue_color"],
            "En retard",
            data["overdue_status"]
        )
        self.content.add_widget(overdue_box)

        parts_box = self._create_status_line(
            data["parts_icon"],
            data["parts_color"],
            "Pièces",
            data["parts_status"]
        )
        self.content.add_widget(parts_box)

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
