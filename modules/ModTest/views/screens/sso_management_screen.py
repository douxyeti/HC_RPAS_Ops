from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText
from kivy.clock import Clock

class SsoManagementScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout racine
        root_layout = MDBoxLayout(
            orientation='vertical',
            md_bg_color=[1, 1, 1, 1],
            padding=dp(20),
            spacing=dp(20)
        )

        # Barre supérieure
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56)
        )

        back_button = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back,
            pos_hint={'center_y': 0.5}
        )

        title_label = MDLabel(
            text="Gestion du SSO (single sign on)",
            bold=True,
            font_size="24sp",
            adaptive_height=True,
            theme_text_color="Primary",
            pos_hint={'center_y': 0.5}
        )

        top_bar.add_widget(back_button)
        top_bar.add_widget(title_label)

        # Label pour le champ de texte
        key_field_label = MDLabel(
            text="Entrez votre clé privé de service Firebase",
            halign="center",
            adaptive_height=True,
            theme_text_color="Secondary"
        )

        # Champ de texte centré
        self.firebase_key_field = MDTextField(
            mode="outlined",
            multiline=True,
            size_hint_x=None,
            width=dp(500),
            pos_hint={'center_x': 0.5},
            helper_text="Collez le contenu du fichier JSON de la clé de service ici.",
            helper_text_mode="on_focus"
        )

        # Bouton de sauvegarde
        save_button = MDButton(
            MDButtonText(text="SAUVEGARDER"),
            pos_hint={'center_x': 0.5},
            on_release=self.trigger_save_key
        )

        # Assemblage
        root_layout.add_widget(top_bar)
        root_layout.add_widget(key_field_label)
        root_layout.add_widget(self.firebase_key_field)
        root_layout.add_widget(save_button)

        # Widget d'espacement pour pousser le contenu vers le haut
        from kivy.uix.widget import Widget
        root_layout.add_widget(Widget())

        self.add_widget(root_layout)

    def go_back(self, *args):
        """Returns to the previous screen."""
        app = MDApp.get_running_app()
        app.root.current = 'specialized_dashboard'

    def trigger_save_key(self, *args):
        """
        Déclenche la logique de sauvegarde de la clé.
        """
        app = MDApp.get_running_app()
        app.logger.info("SSO_SAVE: Clic sur le bouton détecté. Appel direct de save_key.")
        self.save_key()

    def save_key(self, *args):
        """
        Récupère la clé, la chiffre et la publie sur MQTT avec persistance.
        Affiche une boîte de dialogue pour informer l'utilisateur du résultat.
        """
        app = MDApp.get_running_app()
        app.logger.info("SSO_SAVE: Démarrage de la sauvegarde de la clé (planifié).")
        
        key_text = self.firebase_key_field.text

        if not key_text.strip():
            app.logger.warning("SSO_SAVE: Tentative de sauvegarde d'une clé vide.")
            self.show_dialog("Erreur de saisie", "Le champ de la clé ne peut pas être vide.")
            return

        try:
            app.logger.info("SSO_SAVE: Récupération des services.")
            encryption_service = app.encryption_service
            mqtt_service = app.mqtt_service
            config_service = app.config_service
            app.logger.info(f"SSO_SAVE: Services récupérés: encryption={bool(encryption_service)}, mqtt={bool(mqtt_service)}, config={bool(config_service)}")

            if not all([encryption_service, mqtt_service, config_service]):
                app.logger.error("SSO_SAVE: Un ou plusieurs services sont manquants.")
                self.show_dialog("Erreur Système", "Un ou plusieurs services n'ont pas pu être initialisés.")
                return

            app.logger.info(f"SSO_SAVE: Vérification de la connexion MQTT. État : {mqtt_service.connection_state}")
            if mqtt_service.connection_state != 'connected':
                app.logger.error("SSO_SAVE: Le service MQTT n'est pas connecté.")
                self.show_dialog("Erreur de Connexion", "Le service MQTT n'est pas connecté. Vérifiez la configuration.")
                return

            app.logger.info("SSO_SAVE: Chiffrement de la clé.")
            encrypted_key = encryption_service.encrypt(key_text)
            app.logger.info("SSO_SAVE: Clé chiffrée avec succès.")

            app.logger.info("SSO_SAVE: Récupération du topic MQTT.")
            topic = config_service.get_config('mqtt.topics.system.config.sso_key')
            app.logger.info(f"SSO_SAVE: Topic récupéré : {topic}")
            if not topic:
                app.logger.error("SSO_SAVE: Le topic MQTT pour la clé SSO n'est pas défini.")
                self.show_dialog("Erreur de Configuration", "Le topic MQTT pour la clé SSO n'est pas défini.")
                return

            app.logger.info(f"SSO_SAVE: Publication sur le topic '{topic}'.")
            success = mqtt_service.publish(topic, encrypted_key, retain=True)
            app.logger.info(f"SSO_SAVE: Publication terminée. Succès : {success}")

            if success:
                app.logger.info("SSO_SAVE: Affichage du dialogue de succès.")
                self.show_dialog("Opération réussie", "La clé SSO a été chiffrée et sauvegardée avec succès.")
            else:
                app.logger.warning("SSO_SAVE: Affichage du dialogue d'échec de publication.")
                self.show_dialog("Échec", "La publication de la clé sur le serveur MQTT a échoué.")

        except Exception as e:
            app.logger.error(f"SSO_SAVE: Une exception a été levée : {e}", exc_info=True)
            self.show_dialog("Erreur Inattendue", f"Une erreur est survenue : {e}")

    def show_dialog(self, title, text):
        """Affiche une boîte de dialogue modale en utilisant les composants modernes de KivyMD 2.0."""
        # Correction de l'erreur de logique : on crée d'abord le dialogue,
        # puis on assigne les boutons qui le référencent pour éviter un NameError.
        dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogSupportingText(text=text),
        )
        dialog.buttons = [
            MDButton(
                MDButtonText(text="FERMER"),
                style="text",
                on_release=lambda x: dialog.dismiss(),
            ),
        ]
        dialog.open()
