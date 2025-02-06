from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField
from app.services.roles_manager_service import RolesManagerService

class RoleCard(MDCard):
    def __init__(self, role_data, on_edit, on_delete, **kwargs):
        super().__init__(**kwargs)
        print(f"Création de la carte pour le rôle : {role_data}")  # Debug
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.elevation = 1
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(orientation='horizontal', adaptive_height=True)
        
        # Titre avec vérification
        title_text = role_data.get('name', '')
        print(f"Titre du rôle : {title_text}")  # Debug
        
        title = MDLabel(
            text=title_text,
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
        
        edit_btn = MDIconButton(
            icon='pencil',
            on_release=lambda x: on_edit(role_data)
        )
        delete_btn = MDIconButton(
            icon='delete',
            on_release=lambda x: on_delete(role_data)
        )
        
        actions.add_widget(edit_btn)
        actions.add_widget(delete_btn)
        header.add_widget(actions)
        
        # Description avec vérification
        desc_text = role_data.get('description', 'Aucune description')
        print(f"Description du rôle : {desc_text}")  # Debug
        
        description = MDLabel(
            text=desc_text,
            adaptive_height=True
        )
        
        self.add_widget(header)
        self.add_widget(description)

class RolesManagerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'roles_manager'
        self.roles_manager_service = RolesManagerService()
        self.load_roles()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_roles()  # Recharge les rôles à chaque fois qu'on revient sur l'écran
        
    def load_roles(self):
        """Charge et affiche la liste des rôles"""
        roles_grid = self.ids.roles_grid
        roles_grid.clear_widgets()
        roles = self.roles_manager_service.get_all_roles()
        
        for role_id, role_data in roles.items():
            print(f"Chargement du rôle : ID={role_id}, Nom={role_data.get('name', 'NON DÉFINI')}")
            # Vérifie que le rôle a au moins un nom
            if not role_data.get('name'):
                print(f"Rôle ignoré car sans nom : {role_id}")
                continue
                
            role_data['id'] = role_id
            card = RoleCard(
                role_data,
                on_edit=self.edit_role,
                on_delete=self.delete_role,
                size_hint_x=1
            )
            roles_grid.add_widget(card)
            
    def show_create_role_dialog(self):
        """Affiche un dialogue pour saisir le nom du nouveau rôle"""
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Créer un nouveau rôle",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        self.role_name_field = MDTextField(
            hint_text="Nom du rôle",
            mode="outlined"
        )
        content_container.add_widget(self.role_name_field)
        dialog.add_widget(content_container)
        
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        confirm_button = MDButton(
            style="text",
            on_release=lambda x: self.create_role_with_name(dialog)
        )
        confirm_button.add_widget(MDButtonText(text="Créer"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(confirm_button)
        dialog.add_widget(button_container)
        
        dialog.open()

    def create_role_with_name(self, dialog):
        """Crée un nouveau rôle avec le nom saisi"""
        role_name = self.role_name_field.text
        if role_name.strip():
            role_data = {
                'name': role_name,
                'description': 'Description du rôle',
                'tasks': []
            }
            self.roles_manager_service.create_role(role_data)
            self.load_roles()
            dialog.dismiss()

    def add_role(self):
        """Affiche le dialogue de création d'un nouveau rôle"""
        self.show_create_role_dialog()

    def edit_role(self, role_data):
        """Ouvre l'écran d'édition pour le rôle"""
        edit_screen = self.manager.get_screen('role_edit')
        edit_screen.role_data = role_data.copy()
        self.manager.current = 'role_edit'
        
    def show_delete_confirmation_dialog(self, role_id):
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None),
            height=dp(200)
        )
        
        # Titre du dialogue
        dialog.add_widget(MDDialogHeadlineText(
            text="Confirmation de suppression",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        # Contenu du dialogue
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        content_container.add_widget(MDLabel(
            text="Êtes-vous sûr de vouloir supprimer ce rôle ?",
            theme_text_color="Secondary"
        ))
        dialog.add_widget(content_container)
        
        # Boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Bouton Annuler
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        button_container.add_widget(cancel_button)
        
        # Bouton Confirmer
        confirm_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_delete_role(role_id, dialog)
        )
        confirm_button.add_widget(MDButtonText(text="Confirmer"))
        button_container.add_widget(confirm_button)
        
        dialog.add_widget(button_container)
        dialog.open()

    def confirm_delete_role(self, role_id, dialog):
        dialog.dismiss()
        self.roles_manager_service.delete_role(role_id)
        self.load_roles()

    def delete_role(self, role_data):
        self.show_delete_confirmation_dialog(role_data['id'])
