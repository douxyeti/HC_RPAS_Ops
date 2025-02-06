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
from kivy.uix.widget import Widget
from kivy.clock import Clock

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
        self.roles_service = RolesManagerService()
        self.load_roles()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_roles()  # Recharge les rôles à chaque fois qu'on revient sur l'écran
        
    def load_roles(self):
        """Charge et affiche la liste des rôles"""
        roles_grid = self.ids.roles_grid
        roles_grid.clear_widgets()
        roles = self.roles_service.get_all_roles()
        
        # Convertir le dictionnaire en liste et trier par nom
        sorted_roles = sorted(
            [{'id': role_id, **role_data} for role_id, role_data in roles.items()],
            key=lambda x: x.get('name', '').lower()  # Tri insensible à la casse
        )
        
        for role_data in sorted_roles:
            print(f"Chargement du rôle : ID={role_data['id']}, Nom={role_data.get('name', 'NON DÉFINI')}")
            # Vérifie que le rôle a au moins un nom
            if not role_data.get('name'):
                print(f"Rôle ignoré car sans nom : {role_data['id']}")
                continue
                
            card = RoleCard(
                role_data,
                on_edit=self.edit_role,
                on_delete=self.delete_role,
                size_hint_x=1
            )
            roles_grid.add_widget(card)
            
    def create_role(self):
        # Créer le dialogue avec les composants appropriés de KivyMD 2.0
        self.dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        # Ajouter le titre avec MDDialogHeadlineText
        self.dialog.add_widget(MDDialogHeadlineText(
            text="Création d'un nouveau rôle",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        # Container pour le contenu
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Champs de saisie
        self.title_field = MDTextField(
            hint_text="Titre du rôle",
            mode="outlined",
            size_hint_x=1
        )
        
        self.description_field = MDTextField(
            hint_text="Description du rôle",
            mode="outlined",
            multiline=True,
            size_hint_x=1
        )
        
        content_container.add_widget(self.title_field)
        content_container.add_widget(self.description_field)
        self.dialog.add_widget(content_container)
        
        # Container pour les boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: self.dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        create_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_create(self.title_field.text, self.description_field.text)
        )
        create_button.add_widget(MDButtonText(text="Créer"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(create_button)
        self.dialog.add_widget(button_container)
        
        self.dialog.open()
        
    def confirm_create(self, title, description):
        """Crée effectivement le rôle avec les informations saisies"""
        if title.strip():  # Vérifie que le titre n'est pas vide
            role_data = {
                'name': title,
                'description': description if description.strip() else 'Aucune description',
                'tasks': []
            }
            self.roles_service.create_role(role_data)
            self.load_roles()
            self.dialog.dismiss()
        
    def edit_role(self, role_data):
        """Ouvre l'écran d'édition pour le rôle"""
        edit_screen = self.manager.get_screen('role_edit')
        edit_screen.role_data = role_data.copy()
        self.manager.current = 'role_edit'
        
    def delete_role(self, role_data):
        # Créer le contenu du dialogue
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(20), dp(20), dp(20), dp(20)],  # [left, top, right, bottom]
            size_hint_y=None,
            height=dp(120)
        )
        
        content.add_widget(
            MDLabel(
                text=f"Supprimer le rôle '{role_data.get('name')}'?",
                theme_font_size="Custom",
                font_size="16sp"
            )
        )
        content.add_widget(
            MDLabel(
                text="Cette action est irréversible.",
                theme_font_size="Custom",
                font_size="14sp"
            )
        )

        # Créer la boîte de dialogue
        self.confirm_dialog = MDDialog(
            radius=20,
            size_hint=(0.8, None),
            height=dp(200)
        )
        
        # Ajouter le contenu
        self.confirm_dialog.add_widget(content)
        
        # Créer les boutons
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        confirm_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_delete(role_data)
        )
        confirm_button.add_widget(MDButtonText(text="Confirmer"))
        
        # Ajouter les boutons
        buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
            pos_hint={'center_x': .5}
        )
        buttons_box.add_widget(cancel_button)
        buttons_box.add_widget(confirm_button)
        self.confirm_dialog.add_widget(buttons_box)
        
        self.confirm_dialog.open()
    
    def confirm_delete(self, role_data):
        """Supprime effectivement le rôle après confirmation"""
        role_id = role_data.get('id')
        if role_id:
            self.roles_service.delete_role(role_id)
            self.load_roles()
        self.confirm_dialog.dismiss()
        self.role_to_delete = None
