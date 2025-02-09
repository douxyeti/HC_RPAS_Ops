from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
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
        self.role_form = None
        self.name_field = None
        self.description_field = None
        self.current_role = None

    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_roles()

    def load_roles(self):
        """Charge et affiche la liste des rôles"""
        print("[DEBUG] RolesManagerScreen.load_roles - Début du chargement")
        roles = self.roles_manager_service.get_all_roles()
        print(f"[DEBUG] RolesManagerScreen.load_roles - Rôles chargés: {[role.get('id', 'NO_ID') for role in roles]}")
        self.display_roles(roles)
            
    def display_roles(self, roles):
        """Affiche la liste des rôles donnée"""
        print("[DEBUG] RolesManagerScreen.display_roles - Début de l'affichage")
        print(f"[DEBUG] RolesManagerScreen.display_roles - Nombre de rôles à afficher: {len(roles)}")
        
        # Effacer les rôles existants
        print("[DEBUG] RolesManagerScreen.display_roles - Effacement des widgets existants")
        self.ids.roles_container.clear_widgets()
        
        # Trier les rôles par ordre alphabétique
        sorted_roles = sorted(roles, key=lambda x: x.get('name', ''))
        print(f"[DEBUG] RolesManagerScreen.display_roles - IDs des rôles triés: {[role.get('id', 'NO_ID') for role in sorted_roles]}")
        
        # Afficher les rôles triés
        for role_data in sorted_roles:
            print(f"[DEBUG] RolesManagerScreen.display_roles - Création de carte pour le rôle: {role_data.get('id', 'NO_ID')}")
            role_card = RoleCard(
                role_data,
                on_edit=self.edit_role,
                on_delete=self.delete_role,
                on_manage_tasks=self.manage_tasks
            )
            self.ids.roles_container.add_widget(role_card)

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

    def show_add_role_dialog(self):
        """Affiche le formulaire pour ajouter un rôle"""
        print("[DEBUG] RolesManagerScreen.show_add_role_dialog - Début")
        
        # Créer ou réutiliser le formulaire
        if not self.role_form:
            self.role_form = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(400, 450),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                padding=20,
                spacing=10
            )
        else:
            # Si le formulaire existe déjà, le nettoyer
            self.role_form.clear_widgets()
        
        # Titre du formulaire
        form_title = MDLabel(
            text="Ajouter un rôle",
            theme_font_size="Custom",
            font_size="24sp",
            halign="center",
            size_hint_y=None,
            height=dp(36)
        )
        
        # Champs de saisie
        self.name_field = MDTextField(
            hint_text="Nom du rôle",
            helper_text="Le nom du rôle est requis",
            helper_text_mode="on_error",
            required=True
        )
        
        self.description_field = MDTextField(
            hint_text="Description",
            multiline=True,
            helper_text="La description est optionnelle"
        )
        
        # Boutons
        buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'center_x': 0.5}
        )
        
        cancel_button = MDButton(
            style="outlined",
            on_release=self.remove_form
        )
        cancel_button.add_widget(MDButtonText(
            text="Annuler",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        save_button = MDButton(
            style="filled",
            on_release=self.add_role
        )
        save_button.add_widget(MDButtonText(
            text="Ajouter",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        buttons_box.add_widget(cancel_button)
        buttons_box.add_widget(save_button)
        
        # Ajouter tous les widgets au formulaire
        self.role_form.add_widget(form_title)
        self.role_form.add_widget(self.name_field)
        self.role_form.add_widget(self.description_field)
        self.role_form.add_widget(buttons_box)
        
        # Ajouter le formulaire à l'écran
        self.add_widget(self.role_form)

    def edit_role(self, role_data):
        """Édite un rôle existant"""
        print(f"[DEBUG] RolesManagerScreen.edit_role - Édition du rôle: {role_data}")
        if not role_data or 'id' not in role_data:
            print("[DEBUG] RolesManagerScreen.edit_role - Erreur: données du rôle invalides")
            return
            
        self.current_role = role_data.copy()  # Make a copy to avoid modifying the original
        self.show_edit_role_dialog()

    def show_edit_role_dialog(self):
        """Affiche le formulaire pour éditer un rôle"""
        print("[DEBUG] RolesManagerScreen.show_edit_role_dialog - Début")
        
        if not self.current_role:
            print("[DEBUG] RolesManagerScreen.show_edit_role_dialog - Erreur: pas de rôle sélectionné")
            return
        
        # Créer le formulaire
        self.role_form = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=(400, 400),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(15),
            spacing=dp(10),
            elevation=4  # Add shadow for better visibility
        )
        
        # Titre du formulaire
        form_title = MDLabel(
            text=f"Modifier le rôle: {self.current_role.get('name', '')}",
            theme_font_size="Custom",
            font_size="24sp",
            adaptive_height=True,
            halign="center"
        )
        
        # Champ pour le nom du rôle
        self.name_field = MDTextField(
            hint_text="Nom du rôle",
            text=self.current_role.get('name', ''),
            helper_text="Le nom du rôle est requis",
            helper_text_mode="on_error",
            required=True,
            mode="outlined"  # Correction : "rectangle" -> "outlined"
        )
        
        # Champ pour la description
        self.description_field = MDTextField(
            hint_text="Description",
            text=self.current_role.get('description', ''),
            multiline=True,
            max_height=100,
            mode="outlined"  # Correction : "rectangle" -> "outlined"
        )
        
        # Conteneur pour les boutons
        buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            adaptive_height=True,
            height=50,
            pos_hint={'center_x': 0.5}
        )
        
        cancel_button = MDButton(
            style="outlined",
            on_release=self.remove_form
        )
        cancel_button.add_widget(MDButtonText(
            text="Annuler",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        save_button = MDButton(
            style="filled",
            on_release=self.update_role
        )
        save_button.add_widget(MDButtonText(
            text="Enregistrer",  # Changed from "Modifier" to "Enregistrer"
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        buttons_box.add_widget(cancel_button)
        buttons_box.add_widget(save_button)
        
        # Ajouter tous les widgets au formulaire
        self.role_form.add_widget(form_title)
        self.role_form.add_widget(self.name_field)
        self.role_form.add_widget(self.description_field)
        self.role_form.add_widget(buttons_box)
        
        # Ajouter le formulaire à l'écran
        self.add_widget(self.role_form)

    def update_role(self, *args):
        """Met à jour un rôle existant"""
        print("[DEBUG] RolesManagerScreen.update_role - Début de la mise à jour")
        if not self.current_role or 'id' not in self.current_role:
            print("[DEBUG] RolesManagerScreen.update_role - Erreur: ID du rôle manquant")
            self.name_field.error = True
            self.name_field.helper_text = "Erreur: impossible de trouver l'ID du rôle"
            return
            
        if not self.name_field.text.strip():
            print("[DEBUG] RolesManagerScreen.update_role - Erreur: nom manquant")
            self.name_field.error = True
            self.name_field.helper_text = "Le nom du rôle est requis"
            return

        # Vérifier si un autre rôle avec le même nom existe déjà
        existing_roles = self.roles_manager_service.get_all_roles()
        if any(role.get('name') == self.name_field.text.strip() 
              and role.get('id') != self.current_role['id'] 
              for role in existing_roles):
            print("[DEBUG] RolesManagerScreen.update_role - Un autre rôle avec ce nom existe déjà")
            self.name_field.error = True
            self.name_field.helper_text = "Un autre rôle avec ce nom existe déjà"
            return
            
        # Utiliser "Aucune description" si le champ est vide
        description = self.description_field.text.strip() or "Aucune description"
        
        # Créer les données du rôle en préservant les tâches et permissions existantes
        role_data = {
            'name': self.name_field.text.strip(),
            'description': description,
            'tasks': self.current_role.get('tasks', []),
            'permissions': self.current_role.get('permissions', [])
        }
        print(f"[DEBUG] RolesManagerScreen.update_role - Données à mettre à jour: {role_data}")
        
        # Mettre à jour le rôle
        if self.roles_manager_service.update_role(self.current_role['id'], role_data):
            print("[DEBUG] RolesManagerScreen.update_role - Mise à jour réussie")
            # Réinitialiser les champs
            self.name_field.text = ""
            self.description_field.text = ""
            self.current_role = None
            
            # Fermer le formulaire et recharger les rôles
            self.remove_form()
            self.load_roles()
        else:
            print("[DEBUG] RolesManagerScreen.update_role - Échec de la mise à jour")
            self.name_field.error = True
            self.name_field.helper_text = "Erreur lors de la mise à jour du rôle"

    def add_role(self, *args):
        """Ajoute un nouveau rôle"""
        print("[DEBUG] RolesManagerScreen.add_role - Début de l'ajout")
        if self.name_field.text:
            # Vérifier si un rôle avec le même nom existe déjà
            existing_roles = self.roles_manager_service.get_all_roles()
            if any(role.get('name') == self.name_field.text for role in existing_roles):
                print("[DEBUG] RolesManagerScreen.add_role - Un rôle avec ce nom existe déjà")
                self.name_field.error = True
                self.name_field.helper_text = "Un rôle avec ce nom existe déjà"
                return
                
            # Utiliser "Aucune description" si le champ est vide
            description = self.description_field.text.strip() or "Aucune description"
            
            # Créer les données du rôle avec un ID unique
            import time
            role_data = {
                'id': str(int(time.time() * 1000)),
                'name': self.name_field.text,
                'description': description,
                'tasks': []  # Liste vide par défaut
            }
            print(f"[DEBUG] RolesManagerScreen.add_role - Données du rôle: {role_data}")
            
            # Ajouter le rôle
            if self.roles_manager_service.create_role(role_data):
                print("[DEBUG] RolesManagerScreen.add_role - Ajout réussi")
                # Réinitialiser les champs
                self.name_field.text = ""
                self.description_field.text = ""
                
                # Fermer le formulaire et recharger les rôles
                self.remove_form()
                self.load_roles()
            else:
                print("[DEBUG] RolesManagerScreen.add_role - Échec de l'ajout")
                self.name_field.error = True
                self.name_field.helper_text = "Erreur lors de l'ajout du rôle"
        else:
            print("[DEBUG] RolesManagerScreen.add_role - Erreur: nom manquant")
            self.name_field.error = True
            self.name_field.helper_text = "Le nom du rôle est requis"

    def remove_form(self, *args):
        """Retire le formulaire de l'écran"""
        if self.role_form:
            self.remove_widget(self.role_form)
            self.role_form = None
            self.name_field = None
            self.description_field = None
            self.current_role = None

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
                style="outlined",
                on_release=lambda x: self.remove_delete_confirmation()
            )
            cancel_button.add_widget(MDButtonText(
                text="Annuler",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            # Bouton Confirmer
            confirm_button = MDButton(
                style="filled",
                on_release=lambda x: self.confirm_delete(role_data['id'])
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
