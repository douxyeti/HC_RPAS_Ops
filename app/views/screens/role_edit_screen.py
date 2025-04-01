from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.snackbar.snackbar import MDSnackbar, MDSnackbarText
from functools import partial
from app.services.roles_manager_service import RolesManagerService

class RoleEditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'role_edit'
        self.role_data = {}
        self.original_data = {}  # Pour détecter les changements
        self.roles_service = RolesManagerService()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        if not hasattr(self, 'role_data') or not self.role_data:
            self.role_data = {}
            
        # Sauvegarder les données originales pour détecter les changements
        self.original_data = self.role_data.copy()
        
        # Remplir les champs
        self.ids.name_field.text = self.role_data.get('name', '')
        self.ids.description_field.text = self.role_data.get('description', '')
        
        # Reset les erreurs
        self.ids.name_field.error = False
        self.ids.description_field.error = False
    
    def validate_fields(self):
        """Valide les champs du formulaire"""
        is_valid = True
        
        # Validation du nom
        if not self.ids.name_field.text.strip():
            self.ids.name_field.error = True
            self.ids.name_field.helper_text = "Le nom du rôle est requis"
            is_valid = False
        else:
            self.ids.name_field.error = False
            
        # La description est optionnelle, pas de validation nécessaire
        self.ids.description_field.error = False
            
        return is_valid
    
    def has_changes(self):
        """Vérifie si des modifications ont été apportées"""
        current_data = {
            'name': self.ids.name_field.text.strip(),
            'description': self.ids.description_field.text.strip()
        }
        return (current_data['name'] != self.original_data.get('name', '') or 
                current_data['description'] != self.original_data.get('description', ''))
    
    def show_snackbar(self, text):
        """Affiche un message temporaire"""
        snackbar = MDSnackbar(
            pos_hint={"center_x": .5, "y": .1},
            size_hint_x=.8
        )
        snackbar.add_widget(MDSnackbarText(
            text=text
        ))
        snackbar.open()
    
    def save_role(self, *args):
        """Sauvegarde les modifications du rôle"""
        if not self.validate_fields():
            self.show_snackbar("Veuillez corriger les erreurs dans le formulaire")
            return
            
        if not self.has_changes():
            self.show_snackbar("Aucune modification n'a été effectuée")
            return
            
        try:
            # Mettre à jour les données du rôle
            self.role_data['name'] = self.ids.name_field.text.strip()
            self.role_data['description'] = self.ids.description_field.text.strip()
            
            # Sauvegarder les modifications dans la base de données
            if self.roles_service.update_role(self.role_data.get('id'), self.role_data):
                self.show_snackbar("Rôle sauvegardé avec succès")
                self.manager.current = 'roles_manager'
            else:
                self.show_snackbar("Erreur lors de la sauvegarde")
            
        except Exception as e:
            self.show_snackbar(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def cancel_edit(self, *args):
        """Annule l'édition et retourne à l'écran précédent"""
        if self.has_changes():
            self.show_snackbar("Modifications annulées")
        self.manager.current = 'roles_manager'  # Retourne à l'écran de la liste des rôles
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Layout principal
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Titre
        title = MDLabel(
            text="Édition du rôle",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # Champs d'édition
        self.name_field = MDTextField(
            id='name_field',
            hint_text="Nom du rôle",
            helper_text="Entrez le nom du rôle",
            helper_text_mode="on_error",
            required=True
        )
        layout.add_widget(self.name_field)
        
        self.description_field = MDTextField(
            id='description_field',
            hint_text="Description",
            helper_text="Entrez la description du rôle",
            helper_text_mode="on_error",
            multiline=True
        )
        layout.add_widget(self.description_field)
        
        # Boutons
        buttons_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(1, None),
            height=50,
            padding=[0, 20, 0, 0]
        )
        
        save_button = MDButton(
            text="Enregistrer",
            on_release=self.save_role
        )
        cancel_button = MDButton(
            text="Annuler",
            on_release=self.cancel_edit
        )
        
        buttons_layout.add_widget(save_button)
        buttons_layout.add_widget(cancel_button)
        layout.add_widget(buttons_layout)
        
        # Ajouter le layout principal à l'écran
        self.add_widget(layout)
