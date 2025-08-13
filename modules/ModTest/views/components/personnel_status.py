"""Composant d'affichage du statut du personnel"""

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

class PersonnelStatus(BaseComponent):
    """Composant d'affichage du statut du personnel"""

    def __init__(self, **kwargs):
        """Initialisation du composant"""
        super().__init__(
            title="État du Personnel",
            icon="account-group",
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
            "active_status": "4 en service",
            "active_color": "green",
            "active_icon": "account-check",
            "training_status": "2 en formation",
            "training_color": "blue",
            "training_icon": "school",
            "leave_status": "1 en congé",
            "leave_color": "yellow",
            "leave_icon": "beach",
            "certification_status": "Tous à jour",
            "certification_color": "green",
            "certification_icon": "certificate"
        })

    def update_content(self, data):
        """Mise à jour du contenu du composant"""
        self.content.clear_widgets()

        # Statuts
        active_box = self._create_status_line(
            data["active_icon"],
            data["active_color"],
            "En service",
            data["active_status"]
        )
        self.content.add_widget(active_box)

        training_box = self._create_status_line(
            data["training_icon"],
            data["training_color"],
            "Formation",
            data["training_status"]
        )
        self.content.add_widget(training_box)

        leave_box = self._create_status_line(
            data["leave_icon"],
            data["leave_color"],
            "Congés",
            data["leave_status"]
        )
        self.content.add_widget(leave_box)

        certification_box = self._create_status_line(
            data["certification_icon"],
            data["certification_color"],
            "Certifications",
            data["certification_status"]
        )
        self.content.add_widget(certification_box)

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
