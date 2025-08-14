from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

from app.services.procedures_manager_service import ProceduresManagerService

class ProceduresManagerScreen(MDScreen):
    """Écran de gestion des procédures"""
    
    def __init__(self, procedures_manager_service, **kwargs):
        super().__init__(**kwargs)
        self.name = 'procedures_manager'
        self.procedures_manager_service = procedures_manager_service
        
        # Initialiser les composants du formulaire
        self.procedure_form = None
        self.step_form = None
        self.name_field = None
        self.description_field = None
        self.duration_field = None
        self.current_procedure = None
        self.current_step = None
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_procedures()
        
    def load_procedures(self):
        """Charge et affiche la liste des procédures"""
        procedures = self.procedures_manager_service.get_all_procedures()
        self.display_procedures(procedures)
        
    def display_procedures(self, procedures):
        """Affiche la liste des procédures"""
        container = self.ids.procedures_container
        container.clear_widgets()
        
        for procedure in procedures:
            card = self.create_procedure_card(procedure, self.manage_steps)
            container.add_widget(card)
            
    def create_procedure_card(self, procedure_data, on_manage_steps):
        """Crée une carte pour une procédure"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=0.95,
            height=dp(100),
            padding=dp(8),
            spacing=dp(4),
            elevation=1,
            md_bg_color=[0.9, 0.9, 1, 1]  # Fond bleu très clair
        )
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True
        )
        
        # Titre
        title = MDLabel(
            text=procedure_data.get('name', ''),
            theme_font_size="Custom",
            font_size="20sp",
            adaptive_height=True
        )
        header.add_widget(title)
        
        # Boutons d'action
        actions = MDBoxLayout(
            orientation='horizontal',
            adaptive_width=True,
            spacing=dp(8)
        )
        
        # Bouton d'édition
        edit_btn = MDIconButton(
            icon='pencil',
            on_release=lambda x: self.edit_procedure(procedure_data)
        )
        actions.add_widget(edit_btn)
        
        # Bouton de gestion des étapes
        steps_btn = MDIconButton(
            icon='clipboard-list',
            on_release=lambda x: on_manage_steps(procedure_data),
            theme_icon_color="Custom",
            icon_color=[0, 0, 1, 1]  # Bleu
        )
        actions.add_widget(steps_btn)
        
        # Bouton de suppression
        delete_btn = MDIconButton(
            icon='delete',
            on_release=lambda x: self.delete_procedure(procedure_data),
            theme_icon_color="Custom",
            icon_color=[1, 0, 0, 1]  # Rouge
        )
        actions.add_widget(delete_btn)
        
        header.add_widget(actions)
        
        # Description
        description = MDLabel(
            text=procedure_data.get('description', 'Aucune description'),
            adaptive_height=True
        )
        
        card.add_widget(header)
        card.add_widget(description)
        
        return card
        
    def create_step_card(self, step_data):
        """Crée une carte pour une étape"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=0.95,
            height=dp(120),  # Augmenté pour accommoder les boutons
            padding=dp(8),
            spacing=dp(4),
            elevation=1,
            md_bg_color=[0.9, 0.9, 1, 1]  # Fond bleu très clair
        )
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True
        )
        
        # Layout pour le numéro d'ordre et le titre
        title_layout = MDBoxLayout(
            orientation='horizontal',
            adaptive_height=True,
            spacing=dp(8)
        )
        
        # Numéro d'ordre
        order = MDLabel(
            text=f"#{step_data.get('order', '?')}",
            size_hint_x=None,
            width=dp(30),
            theme_font_size="Custom",
            font_size="18sp"
        )
        title_layout.add_widget(order)
        
        # Titre
        title = MDLabel(
            text=step_data.get('name', ''),
            theme_font_size="Custom",
            font_size="20sp",
            adaptive_height=True
        )
        title_layout.add_widget(title)
        header.add_widget(title_layout)
        
        # Boutons d'action
        actions = MDBoxLayout(
            orientation='horizontal',
            adaptive_width=True,
            spacing=dp(8)
        )
        
        # Boutons de réorganisation
        up_btn = MDIconButton(
            icon='arrow-up',
            on_release=lambda x: self.move_step_up(step_data),
            theme_icon_color="Custom",
            icon_color=[0, 0, 1, 1]  # Bleu
        )
        actions.add_widget(up_btn)
        
        down_btn = MDIconButton(
            icon='arrow-down',
            on_release=lambda x: self.move_step_down(step_data),
            theme_icon_color="Custom",
            icon_color=[0, 0, 1, 1]  # Bleu
        )
        actions.add_widget(down_btn)
        
        # Bouton d'insertion
        insert_btn = MDIconButton(
            icon='plus-box',
            on_release=lambda x: self.insert_step_after(step_data),
            theme_icon_color="Custom",
            icon_color=[0, 0.7, 0, 1]  # Vert
        )
        actions.add_widget(insert_btn)
        
        # Bouton d'édition
        edit_btn = MDIconButton(
            icon='pencil',
            on_release=lambda x: self.edit_step(step_data)
        )
        actions.add_widget(edit_btn)
        
        # Bouton de suppression
        delete_btn = MDIconButton(
            icon='delete',
            on_release=lambda x: self.show_delete_step_confirmation(step_data),
            theme_icon_color="Custom",
            icon_color=[1, 0, 0, 1]  # Rouge
        )
        actions.add_widget(delete_btn)
        
        header.add_widget(actions)
        
        # Description et durée
        info_box = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            spacing=dp(2)
        )
        
        description = MDLabel(
            text=step_data.get('description', 'Aucune description'),
            adaptive_height=True
        )
        info_box.add_widget(description)
        
        duration = MDLabel(
            text=f"Durée : {step_data.get('duration', 0)} minutes",
            theme_font_size="Custom",
            font_size="14sp",
            adaptive_height=True
        )
        info_box.add_widget(duration)
        
        card.add_widget(header)
        card.add_widget(info_box)
        
        return card
        
    def move_step_up(self, step_data):
        """Déplace une étape vers le haut dans la liste"""
        current_order = step_data.get('order', 0)
        if current_order <= 1:
            return  # Déjà en haut
            
        # Récupérer toutes les étapes de la procédure
        steps = self.current_procedure.get('steps', [])
        steps_sorted = sorted(steps, key=lambda x: x.get('order', 0))
        
        # Trouver l'étape précédente
        prev_step = None
        for step in steps_sorted:
            if step.get('order', 0) < current_order:
                prev_step = step
        
        if prev_step:
            # Échanger les ordres
            prev_order = prev_step.get('order', 0)
            step_data['order'] = prev_order
            prev_step['order'] = current_order
            
            # Mettre à jour dans Firebase
            self.procedures_manager_service.update_procedure(self.current_procedure['id'], self.current_procedure)
            self.refresh_steps()

    def move_step_down(self, step_data):
        """Déplace une étape vers le bas dans la liste"""
        current_order = step_data.get('order', 0)
        
        # Récupérer toutes les étapes de la procédure
        steps = self.current_procedure.get('steps', [])
        steps_sorted = sorted(steps, key=lambda x: x.get('order', 0))
        
        # Trouver l'étape suivante
        next_step = None
        for step in reversed(steps_sorted):
            if step.get('order', 0) > current_order:
                next_step = step
                break
        
        if next_step:
            # Échanger les ordres
            next_order = next_step.get('order', 0)
            step_data['order'] = next_order
            next_step['order'] = current_order
            
            # Mettre à jour dans Firebase
            self.procedures_manager_service.update_procedure(self.current_procedure['id'], self.current_procedure)
            self.refresh_steps()

    def insert_step_after(self, step_data):
        """Insère une nouvelle étape après l'étape donnée"""
        current_order = step_data.get('order', 0)
        
        # Récupérer toutes les étapes de la procédure
        steps = self.current_procedure.get('steps', [])
        steps_sorted = sorted(steps, key=lambda x: x.get('order', 0))
        
        # Décaler toutes les étapes après le point d'insertion
        for step in reversed(steps_sorted):
            if step.get('order', 0) >= current_order:
                step['order'] = step.get('order', 0) + 1
        
        # Préparer la nouvelle étape
        self.current_step = None
        self.new_step_order = current_order
        self.show_add_step_dialog()
        
    def show_add_procedure_dialog(self):
        """Affiche le formulaire pour ajouter une procédure"""
        self.current_procedure = None
        self.show_procedure_form("Nouvelle procédure")
        
    def show_procedure_form(self, title, procedure=None):
        """Affiche le formulaire pour ajouter ou modifier une procédure."""
        
        # Créer une carte pour le dialogue
        dialog_card = MDCard(
            size_hint=(0.8, None),
            height=dp(300),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(10),
            spacing=dp(10)
        )

        # Layout vertical pour le contenu
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True
        )

        # Titre
        title_label = MDLabel(
            text=title,
            theme_font_size="Custom",
            font_size="24sp",
            bold=True,
            adaptive_height=True
        )
        content.add_widget(title_label)

        # Champs de texte
        name_field = MDTextField(
            hint_text="Nom de la procédure",
            mode="outlined",
            text=procedure.get('name', '') if procedure else ""
        )
        content.add_widget(name_field)

        description_field = MDTextField(
            hint_text="Description",
            mode="outlined",
            text=procedure.get('description', '') if procedure else "",
            multiline=True
        )
        content.add_widget(description_field)

        # Boutons
        buttons_box = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )

        cancel_button = MDButton(
            style="outlined",
            on_release=lambda x: dialog_card.parent.remove_widget(dialog_card)
        )
        cancel_button.add_widget(MDButtonText(text="ANNULER"))
        buttons_box.add_widget(cancel_button)

        save_button = MDButton(
            style="filled",
            on_release=lambda x: self.save_procedure_and_close(
                name_field.text,
                description_field.text,
                procedure.get('id') if procedure else None,
                dialog_card
            )
        )
        save_button.add_widget(MDButtonText(text="SAUVEGARDER"))
        buttons_box.add_widget(save_button)

        content.add_widget(buttons_box)
        dialog_card.add_widget(content)

        # Ajouter la carte à l'écran
        self.add_widget(dialog_card)
        self.procedure_form = dialog_card

    def save_procedure_and_close(self, name, description, procedure_id, dialog):
        """Sauvegarde la procédure et ferme le dialogue"""
        self.save_procedure(name, description, procedure_id)
        dialog.parent.remove_widget(dialog)

    def save_procedure(self, name, description, procedure_id=None):
        """Sauvegarde une procédure"""
        procedure_data = {
            'name': name.strip(),
            'description': description.strip()
        }
        
        if procedure_id:
            self.procedures_manager_service.update_procedure(
                procedure_id,
                procedure_data
            )
        else:
            self.procedures_manager_service.create_procedure(procedure_data)
            
        self.load_procedures()
        
    def edit_procedure(self, procedure_data):
        """Édite une procédure existante"""
        self.current_procedure = procedure_data
        self.show_procedure_form("Modifier la procédure", procedure_data)
        
    def delete_procedure(self, procedure_data):
        """Supprime une procédure"""
        self.current_procedure = procedure_data
        self.show_delete_confirmation()
        
    def show_delete_confirmation(self):
        """Affiche la confirmation de suppression"""
        self.delete_dialog = MDCard(
            size_hint=(0.8, None),
            height=dp(200),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(10),
            spacing=dp(10)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True
        )
        
        title_label = MDLabel(
            text="Confirmer la suppression",
            theme_font_size="Custom",
            font_size="24sp",
            bold=True,
            adaptive_height=True
        )
        content.add_widget(title_label)
        
        text_label = MDLabel(
            text=f"Voulez-vous vraiment supprimer la procédure '{self.current_procedure['name']}' ?",
            adaptive_height=True
        )
        content.add_widget(text_label)
        
        buttons_box = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )
        
        cancel_button = MDButton(
            style="outlined",
            on_release=lambda x: self.delete_dialog.parent.remove_widget(self.delete_dialog)
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        buttons_box.add_widget(cancel_button)
        
        confirm_button = MDButton(
            style="filled",
            on_release=lambda x: self.confirm_delete_and_close(self.delete_dialog)
        )
        confirm_button.add_widget(MDButtonText(text="Supprimer"))
        buttons_box.add_widget(confirm_button)
        
        content.add_widget(buttons_box)
        self.delete_dialog.add_widget(content)
        
        self.add_widget(self.delete_dialog)
        
    def confirm_delete_and_close(self, dialog):
        """Confirme et exécute la suppression"""
        if self.current_procedure:
            self.procedures_manager_service.delete_procedure(self.current_procedure['id'])
            self.current_procedure = None
            self.load_procedures()
        dialog.parent.remove_widget(dialog)
        
    def remove_delete_confirmation(self, *args):
        """Ferme la boîte de dialogue de confirmation"""
        if hasattr(self, 'delete_dialog'):
            self.delete_dialog.parent.remove_widget(self.delete_dialog)
            
    def remove_form(self, *args):
        """Retire le formulaire de l'écran"""
        if self.procedure_form:
            self.procedure_form.parent.remove_widget(self.procedure_form)
        if self.step_form:
            self.step_form.parent.remove_widget(self.step_form)
            
    def manage_steps(self, procedure_data):
        """Gère les étapes d'une procédure"""
        self.current_procedure = procedure_data
        
        # Afficher le conteneur des étapes
        steps_view = self.ids.steps_view
        steps_view.opacity = 1
        steps_view.height = dp(400)  # Hauteur fixe pour le conteneur des étapes
        
        # Masquer le conteneur des procédures
        self.ids.procedures_container.parent.opacity = 0
        self.ids.procedures_container.parent.height = 0
        
        # Afficher les étapes
        self.display_steps(procedure_data.get('steps', []))
        
    def display_steps(self, steps):
        """Affiche la liste des étapes"""
        container = self.ids.steps_container
        container.clear_widgets()
        
        for step in sorted(steps, key=lambda x: x.get('order', 0)):
            card = self.create_step_card(step)
            container.add_widget(card)
            
    def show_add_step_dialog(self):
        """Affiche le formulaire pour ajouter une étape"""
        if not self.current_procedure:
            return
        self.current_step = None
        self.show_step_form("Nouvelle étape")
        
    def show_step_form(self, title):
        """Affiche le formulaire d'étape"""
        dialog_card = MDCard(
            size_hint=(0.8, None),
            height=dp(300),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(10),
            spacing=dp(10)
        )

        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True
        )

        # Titre
        title_label = MDLabel(
            text=title,
            theme_font_size="Custom",
            font_size="24sp",
            bold=True,
            adaptive_height=True
        )
        content.add_widget(title_label)

        # Champs de texte
        name_field = MDTextField(
            hint_text="Nom de l'étape",
            mode="outlined",
            text=self.current_step.get('name', '') if self.current_step else ""
        )
        content.add_widget(name_field)

        description_field = MDTextField(
            hint_text="Description",
            mode="outlined",
            text=self.current_step.get('description', '') if self.current_step else "",
            multiline=True
        )
        content.add_widget(description_field)

        duration_field = MDTextField(
            hint_text="Durée (minutes)",
            mode="outlined",
            text=str(self.current_step.get('duration', '')) if self.current_step else "",
            input_filter='int'
        )
        content.add_widget(duration_field)

        # Boutons
        buttons_box = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10),
            padding=[0, dp(10), 0, 0]
        )

        cancel_button = MDButton(
            style="outlined",
            on_release=lambda x: dialog_card.parent.remove_widget(dialog_card)
        )
        cancel_button.add_widget(MDButtonText(text="ANNULER"))
        buttons_box.add_widget(cancel_button)

        save_button = MDButton(
            style="filled",
            on_release=lambda x: self.save_step(
                name_field.text,
                description_field.text,
                duration_field.text,
                dialog_card
            )
        )
        save_button.add_widget(MDButtonText(text="SAUVEGARDER"))
        buttons_box.add_widget(save_button)

        content.add_widget(buttons_box)
        dialog_card.add_widget(content)

        # Ajouter la carte à l'écran
        self.add_widget(dialog_card)
        self.step_form = dialog_card
        
    def save_step(self, name, description, duration, dialog):
        """Sauvegarde une étape"""
        try:
            duration = int(duration) if duration.strip() else 0
        except ValueError:
            duration = 0

        step_data = {
            'name': name.strip(),
            'description': description.strip(),
            'duration': duration
        }

        if self.current_step:
            # Mode édition
            self.procedures_manager_service.update_step(
                self.current_procedure['id'],
                self.current_step['id'],
                step_data
            )
        else:
            # Mode création - ajouter l'ordre si défini
            if hasattr(self, 'new_step_order'):
                step_data['order'] = self.new_step_order
            self.procedures_manager_service.add_step(
                self.current_procedure['id'],
                step_data
            )

        # Recharger la procédure pour mettre à jour l'affichage
        updated_procedure = self.procedures_manager_service.get_procedure(self.current_procedure['id'])
        if updated_procedure:
            self.current_procedure = updated_procedure
            self.display_steps(updated_procedure.get('steps', []))

        # Fermer le formulaire
        dialog.parent.remove_widget(dialog)
        
    def edit_step(self, step_data):
        """Édite une étape existante"""
        self.current_step = step_data
        self.show_step_form("Modifier l'étape")
        
    def delete_step(self, step_data):
        """Supprime une étape"""
        if self.current_procedure:
            procedure_id = self.current_procedure['id']
            self.procedures_manager_service.delete_step(
                procedure_id,
                step_data['id']
            )
            # Mettre à jour la procédure actuelle
            updated_procedure = self.procedures_manager_service.get_procedure(procedure_id)
            if updated_procedure:
                self.current_procedure = updated_procedure
                self.display_steps(updated_procedure.get('steps', []))
            
    def go_back(self):
        """Retourne à l'écran précédent"""
        if self.ids.steps_view.opacity == 1:
            # Si on est dans la vue des étapes, retourner à la liste des procédures
            self.ids.steps_view.opacity = 0
            self.ids.steps_view.height = 0
            self.ids.procedures_container.parent.opacity = 1
            self.ids.procedures_container.parent.height = dp(400)  # Hauteur fixe pour le conteneur des procédures
            self.current_procedure = None
            self.current_step = None
        else:
            # Sinon, retourner au tableau de bord spécialisé
            self.manager.current = "specialized_dashboard"

    def refresh_steps(self):
        """Rafraîchit l'affichage des étapes"""
        if self.current_procedure:
            # Récupérer la procédure mise à jour
            updated_procedure = self.procedures_manager_service.get_procedure(self.current_procedure['id'])
            if updated_procedure:
                self.current_procedure = updated_procedure
                self.display_steps(updated_procedure.get('steps', []))

    def show_filter_menu(self, widget):
        """Affiche le menu de filtrage des procédures"""
        # TODO: Implémenter le filtrage des procédures
        pass

    def show_sort_menu(self, widget):
        """Affiche le menu de tri des procédures"""
        # TODO: Implémenter le tri des procédures
        pass

    def show_delete_step_confirmation(self, step_data):
        """Affiche la confirmation de suppression d'une étape"""
        self.current_step = step_data
        
        # Créer la carte de confirmation
        if not hasattr(self, 'confirm_delete_card'):
            confirm_card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(400, 200),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                padding=dp(15),
                spacing=dp(10)
            )
            
            # Titre
            title = MDLabel(
                text=f"Supprimer l'étape '{step_data.get('name')}'?",
                theme_font_size="Custom",
                font_size="20sp",
                adaptive_height=True
            )
            confirm_card.add_widget(title)
            
            # Message d'avertissement
            warning = MDLabel(
                text="Cette action est irréversible. Êtes-vous sûr de vouloir supprimer cette étape ?",
                theme_font_size="Custom",
                font_size="14sp",
                adaptive_height=True
            )
            confirm_card.add_widget(warning)
            
            # Conteneur pour les boutons
            buttons_container = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                spacing=dp(10),
                pos_hint={'right': 1}
            )
            
            # Bouton Annuler
            cancel_button = MDButton(
                style="outlined",
                on_release=lambda x: self.remove_delete_step_confirmation()
            )
            cancel_button.add_widget(MDButtonText(
                text="Annuler",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            # Bouton Confirmer
            confirm_button = MDButton(
                style="filled",
                on_release=lambda x: self.confirm_delete_step_and_close()
            )
            confirm_button.add_widget(MDButtonText(
                text="Confirmer",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            buttons_container.add_widget(cancel_button)
            buttons_container.add_widget(confirm_button)
            confirm_card.add_widget(buttons_container)
            
            # Stocker la référence à la carte
            self.confirm_delete_card = confirm_card
            
            # Ajouter la carte à l'écran
            self.add_widget(confirm_card)

    def remove_delete_step_confirmation(self):
        """Retire la carte de confirmation de suppression"""
        if hasattr(self, 'confirm_delete_card'):
            self.remove_widget(self.confirm_delete_card)
            delattr(self, 'confirm_delete_card')

    def confirm_delete_step_and_close(self):
        """Confirme et exécute la suppression de l'étape"""
        if self.current_step and self.current_procedure:
            # Supprimer l'étape via le service
            self.procedures_manager_service.delete_step(
                self.current_procedure['id'],
                self.current_step['id']
            )
            
            # Retirer la carte de confirmation
            self.remove_delete_step_confirmation()
            
            # Mettre à jour la procédure actuelle et recharger les étapes
            updated_procedure = self.procedures_manager_service.get_procedure(self.current_procedure['id'])
            if updated_procedure:
                self.current_procedure = updated_procedure
                self.display_steps(updated_procedure.get('steps', []))
