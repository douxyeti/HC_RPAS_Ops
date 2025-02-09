from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from app.services.roles_manager_service import RolesManagerService

class RoleCard(MDCard):
    def __init__(self, role_data, on_edit, on_delete, on_manage_tasks, **kwargs):
        super().__init__(**kwargs)
        print(f"Création de la carte pour le rôle : {role_data}")  # Debug
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.size_hint_x = 0.95
        self.height = dp(100)
        self.padding = dp(8)
        self.spacing = dp(4)
        self.elevation = 1
        self.md_bg_color = [0.9, 0.9, 1, 1]  # Fond bleu très clair
        
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
        actions.add_widget(edit_btn)

        # Bouton de gestion des tâches
        tasks_btn = MDIconButton(
            icon='clipboard-list',
            on_release=lambda x: on_manage_tasks(role_data),
            theme_icon_color="Custom",
            icon_color=[1, 0, 0, 1]  # Rouge
        )
        actions.add_widget(tasks_btn)
        
        delete_btn = MDIconButton(
            icon='delete',
            on_release=lambda x: on_delete(role_data)
        )
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
    """Écran de gestion des rôles"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'roles_manager'
        self.roles_manager_service = RolesManagerService()
        
        # Initialiser les composants du formulaire
        self.role_dialog = None
        self.name_field = None
        self.description_field = None
        self.current_role = None

    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_roles()

    def load_roles(self):
        """Charge et affiche la liste des rôles"""
        # Effacer les rôles existants
        self.ids.roles_container.clear_widgets()
        
        # Obtenir les rôles
        roles = self.roles_manager_service.get_all_roles()
        self.display_roles(roles)
            
    def display_roles(self, roles):
        """Affiche la liste des rôles donnée"""
        self.ids.roles_container.clear_widgets()
        for role in roles:
            card = RoleCard(
                role_data=role,
                on_edit=self.edit_role,
                on_delete=self.delete_role,
                on_manage_tasks=self.manage_tasks
            )
            self.ids.roles_container.add_widget(card)

    def show_menu(self, items, caller=None):
        """Affiche un menu déroulant"""
        menu = MDDropdownMenu(
            caller=caller,
            items=items,
            width_mult=4,
            max_height=dp(250),
            radius=[8, 8, 8, 8],
            background_color=[0.9, 0.9, 1, 1]
        )
        menu.open()

    def show_filter_menu(self, button):
        """Affiche le menu de filtrage des rôles"""
        menu_items = [
            {
                "text": "Tous les rôles",
                "on_release": lambda x="all": self.filter_roles(x),
            },
            {
                "text": "Opérations",
                "on_release": lambda x="operations": self.filter_roles(x),
            },
            {
                "text": "Formation",
                "on_release": lambda x="formation": self.filter_roles(x),
            },
            {
                "text": "Maintenance",
                "on_release": lambda x="maintenance": self.filter_roles(x),
            }
        ]
        self.show_menu(menu_items, button)

    def show_sort_menu(self, button):
        """Affiche le menu de tri des rôles"""
        menu_items = [
            {
                "text": "Par nom (A-Z)",
                "on_release": lambda x="name_asc": self.sort_roles(x),
            },
            {
                "text": "Par nom (Z-A)",
                "on_release": lambda x="name_desc": self.sort_roles(x),
            }
        ]
        self.show_menu(menu_items, button)

    def filter_roles(self, filter_type):
        """Filtre les rôles selon le type"""
        if filter_type == "all":
            self.load_roles()
        else:
            filtered_roles = [
                role for role in self.roles_manager_service.get_all_roles()
                if any(filter_type in perm for perm in role.get('permissions', []))
            ]
            self.display_roles(filtered_roles)

    def sort_roles(self, sort_type):
        """Trie les rôles selon le critère"""
        roles = self.roles_manager_service.get_all_roles()
        if sort_type == "name_asc":
            roles.sort(key=lambda x: x.get('name', ''))
        elif sort_type == "name_desc":
            roles.sort(key=lambda x: x.get('name', ''), reverse=True)
        self.display_roles(roles)

    def refresh_roles(self, *args):
        """Rafraîchit la liste des rôles"""
        self.load_roles()

    def show_add_role_dialog(self, *args):
        print("Début de l'ajout de rôle")  # Log 1
        try:
            if not self.role_dialog:
                print("Création des champs de texte")  # Log 2
                
                # Créer le formulaire avec MDCard
                form_card = MDCard(
                    orientation='vertical',
                    size_hint=(None, None),
                    size=(400, 300),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    padding=dp(15),
                    spacing=dp(10)
                )
                
                # Ajouter un titre
                title = MDLabel(
                    text="Ajouter un rôle",
                    theme_font_size="Custom",
                    font_size="24sp",
                    adaptive_height=True
                )
                form_card.add_widget(title)
                
                # Créer les champs de texte
                self.name_field = MDTextField(
                    hint_text="Nom du rôle",
                    helper_text="Entrez le nom du rôle",
                    helper_text_mode="on_error"
                )
                print("Champ name_field créé")  # Log 3
                
                self.description_field = MDTextField(
                    hint_text="Description du rôle",
                    helper_text="Entrez la description du rôle",
                    helper_text_mode="on_error",
                    multiline=True
                )
                print("Champ description_field créé")  # Log 4
                
                # Ajouter les champs au formulaire
                form_card.add_widget(self.name_field)
                form_card.add_widget(self.description_field)
                
                # Créer un conteneur pour les boutons
                buttons_container = MDBoxLayout(
                    orientation='horizontal',
                    adaptive_height=True,
                    spacing=dp(10),
                    pos_hint={'right': 1}
                )
                
                # Créer les boutons
                cancel_button = MDButton(
                    style="text",
                    on_release=lambda x: self.remove_form()
                )
                cancel_button.add_widget(MDButtonText(text="Annuler"))
                
                add_button = MDButton(
                    style="filled",
                    on_release=self.add_role
                )
                add_button.add_widget(MDButtonText(text="Ajouter"))
                
                buttons_container.add_widget(cancel_button)
                buttons_container.add_widget(add_button)
                form_card.add_widget(buttons_container)
                
                # Stocker la référence au formulaire
                self.role_dialog = form_card
                
                # Ajouter le formulaire à l'écran
                self.add_widget(form_card)
                print("Formulaire créé et ajouté")  # Log 8
            
        except Exception as e:
            print(f"ERREUR dans l'ajout de rôle: {str(e)}")  # Log d'erreur
            
    def remove_form(self):
        if self.role_dialog:
            self.remove_widget(self.role_dialog)
            self.role_dialog = None

    def add_role(self, *args):
        """Ajoute un nouveau rôle"""
        if self.name_field.text and self.description_field.text:
            # Générer un ID unique basé sur un timestamp
            import time
            role_id = str(int(time.time() * 1000))
            
            role_data = {
                'id': role_id,
                'name': self.name_field.text,
                'description': self.description_field.text,
                'tasks': []  # Initialize empty tasks list
            }
            
            # Ajouter le rôle via le service
            if self.roles_manager_service.create_role(role_data):
                # Réinitialiser les champs
                self.name_field.text = ""
                self.description_field.text = ""
                
                # Fermer le formulaire et recharger les rôles
                self.remove_form()
                self.load_roles()
            else:
                # Show error in UI
                self.name_field.error = True
                self.name_field.helper_text = "Erreur lors de la création du rôle"
        else:
            if not self.name_field.text:
                self.name_field.error = True
            if not self.description_field.text:
                self.description_field.error = True

    def edit_role(self, role_data):
        """Édite un rôle existant"""
        self.current_role = role_data
        if not self.role_dialog:
            self.show_add_role_dialog()
        
        # Mettre à jour le titre du formulaire
        self.role_dialog.children[0].text = "Modifier le rôle"
        self.name_field.text = role_data.get('name', '')
        self.description_field.text = role_data.get('description', '')
        
        # Changer le texte du bouton
        for child in self.role_dialog.children:
            if isinstance(child, MDBoxLayout) and child.children:
                for grandchild in child.children:
                    if isinstance(grandchild, MDButton) and isinstance(grandchild.children[0], MDButtonText) and grandchild.children[0].text == "Ajouter":
                        grandchild.children[0].text = "Modifier"
                        grandchild.on_release = self.update_role

    def update_role(self, *args):
        """Met à jour un rôle existant"""
        if self.name_field.text and self.description_field.text:
            role_data = {
                'id': self.current_role.get('id'),
                'name': self.name_field.text,
                'description': self.description_field.text
            }
            
            # Mettre à jour le rôle via le service
            self.roles_manager_service.update_role(role_data)
            
            # Réinitialiser les champs
            self.name_field.text = ""
            self.description_field.text = ""
            self.current_role = None
            
            # Fermer le formulaire et recharger les rôles
            self.remove_form()
            self.load_roles()
        else:
            if not self.name_field.text:
                self.name_field.error = True
            if not self.description_field.text:
                self.description_field.error = True

    def delete_role(self, role_data):
        """Supprime un rôle"""
        if not hasattr(self, 'confirm_delete_card'):
            # Créer la carte de confirmation
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
                text=f"Supprimer le rôle '{role_data['name']}' ?",
                theme_font_size="Custom",
                font_size="20sp",
                adaptive_height=True
            )
            confirm_card.add_widget(title)
            
            # Message d'avertissement
            warning = MDLabel(
                text="Cette action est irréversible. Êtes-vous sûr de vouloir supprimer ce rôle ?",
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
                style="text",
                on_release=lambda x: self.remove_delete_confirmation()
            )
            cancel_button.add_widget(MDButtonText(text="Annuler"))
            
            # Bouton Confirmer
            confirm_button = MDButton(
                style="filled",
                on_release=lambda x: self.confirm_delete(role_data['id'])
            )
            confirm_button.add_widget(MDButtonText(text="Confirmer"))
            
            buttons_container.add_widget(cancel_button)
            buttons_container.add_widget(confirm_button)
            confirm_card.add_widget(buttons_container)
            
            # Stocker la référence à la carte
            self.confirm_delete_card = confirm_card
            
            # Ajouter la carte à l'écran
            self.add_widget(confirm_card)
    
    def remove_delete_confirmation(self):
        """Retire la carte de confirmation de suppression"""
        if hasattr(self, 'confirm_delete_card'):
            self.remove_widget(self.confirm_delete_card)
            delattr(self, 'confirm_delete_card')
    
    def confirm_delete(self, role_id):
        """Confirme et exécute la suppression du rôle"""
        # Supprimer le rôle via le service
        self.roles_manager_service.delete_role(role_id)
        
        # Retirer la carte de confirmation
        self.remove_delete_confirmation()
        
        # Recharger la liste des rôles
        self.load_roles()

    def manage_tasks(self, role_data):
        """Gère les tâches pour un rôle spécifique"""
        task_screen = self.manager.get_screen('task_manager')
        task_screen.current_role_id = role_data.get('id')
        task_screen.current_role_name = role_data.get('name')
        self.manager.current = 'task_manager'

    def go_back(self):
        """Retourne à l'écran précédent"""
        self.manager.current = 'dashboard'
