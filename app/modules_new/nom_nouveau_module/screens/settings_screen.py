"""
Écran de configuration du module de base
Cet écran sert de template pour les écrans de configuration des nouveaux modules
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.divider import MDDivider
from kivy.metrics import dp
import logging

logger = logging.getLogger("hc_rpas.nom_nouveau_module.settings_screen")

class SettingsScreen(MDScreen):
    """Écran de configuration du module de base"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        logger.info("Initialisation de l'écran de configuration du module de base")
        
        # Créer le layout principal
        self.layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16)
        )
        
        # Ajouter un titre
        self.title = MDLabel(
            text="Controle_vols - Configuration",
            theme_font_size="Custom",
            font_size="24sp",
            bold=True,
            size_hint_y=None,
            height=dp(36)
        )
        self.layout.add_widget(self.title)
        
        # Conteneur pour les options de configuration
        self.settings_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None
        )
        self.settings_box.bind(minimum_height=self.settings_box.setter('height'))
        
        # Option 1: Nom du module
        self.option1_label = MDLabel(
            text="Nom du module",
            theme_font_size="Custom",
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        self.settings_box.add_widget(self.option1_label)
        
        self.module_name = MDTextField(
            hint_text="Entrez le nom du module",
            helper_text="Le nom affiché dans l'interface",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(48),
            text="Controle_vols"
        )
        self.settings_box.add_widget(self.module_name)
        
        self.settings_box.add_widget(MDDivider())
        
        # Option 2: Paramètres MQTT
        self.option2_label = MDLabel(
            text="Configuration MQTT",
            theme_font_size="Custom",
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        self.settings_box.add_widget(self.option2_label)
        
        self.mqtt_enabled = MDTextField(
            hint_text="Activer MQTT (true/false)",
            helper_text="Permet la communication en temps réel",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(48),
            text="true"
        )
        self.settings_box.add_widget(self.mqtt_enabled)
        
        self.mqtt_topic = MDTextField(
            hint_text="Topic de base MQTT",
            helper_text="Format: hc_rpas/modules/module_id",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(48),
            text="hc_rpas/modules/nom_nouveau_module"
        )
        self.settings_box.add_widget(self.mqtt_topic)
        
        self.settings_box.add_widget(MDDivider())
        
        # Option 3: Paramètres de journalisation
        self.option3_label = MDLabel(
            text="Configuration des logs",
            theme_font_size="Custom",
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        self.settings_box.add_widget(self.option3_label)
        
        self.log_level = MDTextField(
            hint_text="Niveau de log (INFO, DEBUG, WARNING, ERROR)",
            helper_text="Défini la verbosité des logs",
            helper_text_mode="persistent",
            size_hint_y=None,
            height=dp(48),
            text="INFO"
        )
        self.settings_box.add_widget(self.log_level)
        
        # Ajouter le conteneur des paramètres au layout principal
        self.layout.add_widget(self.settings_box)
        
        # Boutons d'action
        self.buttons_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48),
            pos_hint={"right": 1}
        )
        
        # Bouton Annuler
        self.cancel_button = MDButton(
            style="outlined",
            on_release=self.cancel_callback,
            size_hint_x=None,
            width=dp(150)
        )
        self.cancel_button.add_widget(MDButtonText(text="ANNULER"))
        
        # Bouton Sauvegarder
        self.save_button = MDButton(
            style="elevated",
            on_release=self.save_callback,
            size_hint_x=None,
            width=dp(150)
        )
        self.save_button.add_widget(MDButtonText(text="SAUVEGARDER"))
        
        # Ajouter les boutons au conteneur
        self.buttons_box.add_widget(MDBoxLayout())  # Spacer
        self.buttons_box.add_widget(self.cancel_button)
        self.buttons_box.add_widget(self.save_button)
        
        # Ajouter les boutons au layout principal
        self.layout.add_widget(self.buttons_box)
        
        # Ajouter le layout principal à l'écran
        self.add_widget(self.layout)
    
    def cancel_callback(self, instance):
        """Callback pour le bouton Annuler"""
        logger.info("Annulation des modifications")
        # Retourner à l'écran principal
        if self.manager:
            self.manager.current = "main"
    
    def save_callback(self, instance):
        """Callback pour le bouton Sauvegarder"""
        logger.info("Sauvegarde des paramètres")
        
        # Récupérer les valeurs
        module_name = self.module_name.text
        mqtt_enabled = self.mqtt_enabled.text.lower() == "true"
        mqtt_topic = self.mqtt_topic.text
        log_level = self.log_level.text
        
        # Simuler la sauvegarde (à implémenter réellement dans les modules concrets)
        logger.info(f"Paramètres à sauvegarder: nom={module_name}, mqtt={mqtt_enabled}, topic={mqtt_topic}, log={log_level}")
        
        # Retourner à l'écran principal
        if self.manager:
            self.manager.current = "main"
    
    def on_enter(self):
        """Appelé lorsque l'écran devient actif"""
        logger.info("Entrée dans l'écran de configuration du module de base")
    
    def on_leave(self):
        """Appelé lorsque l'écran devient inactif"""
        logger.info("Sortie de l'écran de configuration du module de base")
