"""
Écran d'administration des modules installés.
Permet de visualiser les modules indexés et leurs écrans, et de copier les index pour les utiliser dans les tâches.
"""
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

from app.utils.module_discovery import ModuleDiscovery
import logging

# Ces classes ont été remplacées par une implémentation directe dans la classe ModulesAdminScreen
# pour suivre le modèle utilisé dans le reste de l'application

class ModulesAdminScreen(MDScreen):
    """Écran d'administration des modules installés"""
    
    modules_container = ObjectProperty(None)
    screens_container = ObjectProperty(None)
    index_value = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        print("[DEBUG] ModulesAdminScreen.__init__ - Début de l'initialisation")
        super().__init__(**kwargs)
        
        # Attributs de base
        self.app = App.get_running_app()
        self.selected_module = None
        self.selected_screen = None
        
        # Logger
        self.logger = logging.getLogger("hc_rpas")
        print("[DEBUG] ModulesAdminScreen.__init__ - Logger initialisé")
        
        # Initialiser la découverte de modules à None d'abord
        self.discovery = None
        
        # Utiliser Clock pour initialiser après que tout est prêt
        Clock.schedule_once(self._post_init, 0.5)
    
    def _post_init(self, dt):
        """Initialise la découverte de modules après le chargement de l'écran"""
        try:
            print("[DEBUG] ModulesAdminScreen._post_init - Début de l'initialisation")
            if hasattr(self.app, 'firebase_service') and self.app.firebase_service:
                print("[DEBUG] ModulesAdminScreen._post_init - Firebase service trouvé")
                self.discovery = ModuleDiscovery(self.app.firebase_service)
                print("[DEBUG] ModulesAdminScreen._post_init - ModuleDiscovery initialisé avec succès")
                # Charger les données
                self.refresh_data()
            else:
                print("[ERROR] ModulesAdminScreen._post_init - Firebase service non disponible")
                self.logger.error("Firebase service non disponible pour ModuleDiscovery")
        except Exception as e:
            import traceback
            print(f"[ERROR] ModulesAdminScreen._post_init - Exception: {str(e)}")
            traceback.print_exc()
            self.logger.error(f"Erreur lors de l'initialisation: {str(e)}")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            print("[DEBUG] ModulesAdminScreen.on_enter - Entrée dans l'écran")
            # Si pas encore initialisé, initialiser la découverte
            if self.discovery is None:
                print("[DEBUG] ModulesAdminScreen.on_enter - Discovery non initialisé, appel de _post_init")
                self._post_init(0)
            else:
                print("[DEBUG] ModulesAdminScreen.on_enter - Discovery déjà initialisé, rafraîchissement des données")
                # Rafraîchir les données
                self.refresh_data()
        except Exception as e:
            import traceback
            print(f"[ERROR] ModulesAdminScreen.on_enter - Exception: {str(e)}")
            traceback.print_exc()
    
    def refresh_data(self, *args):
        """Rafraîchit les données des modules"""
        if not self.discovery:
            return
            
        try:
            # Récupérer les modules
            all_modules = self.discovery.get_installed_modules()
            
            # Filtrage STRICT pour n'afficher QUE les modules de développement sans doublons
            filtered_modules = []
            seen_ids = set()  # Pour suivre les IDs déjà vus
            
            for module in all_modules:
                module_id = module.get('id', '')
                module_name = module.get('name', '')
                branch = module.get('branch', '')
                
                # Triple filtrage:
                # 1. Vérifier que c'est une branche de développement
                # 2. Vérifier que l'ID contient 'dev_' aussi (très important)
                # 3. Exclure explicitement tout ce qui contient 'application_principale'
                # 4. Éliminer les doublons basés sur l'ID
                
                if (branch.startswith('dev_') and 
                    'dev_' in module_id and 
                    module_id not in seen_ids and 
                    'application_principale' not in module_id.lower() and
                    'application_principale' not in branch.lower() and
                    'application_principale' not in module_name.lower()):
                    filtered_modules.append(module)
                    seen_ids.add(module_id)
            
            print(f"[DEBUG] ModulesAdminScreen.refresh_data - Total modules: {len(all_modules)}, Après filtrage: {len(filtered_modules)}")
            
            # Vider le conteneur de modules
            self.modules_container.clear_widgets()
            
            # Ajouter les cartes de modules de façon programmatique
            for module in filtered_modules:
                # Créer la carte
                module_card = MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(80),
                    padding=dp(10),
                    spacing=dp(4),
                    md_bg_color=[1, 1, 1, 1],
                    elevation=1,
                    radius=dp(8)
                )
                
                # Conserver les informations dans la carte
                module_card.id = module.get('id', '')
                module_card.name = module.get('name', 'Module sans nom')
                module_card.version = module.get('version', '1.0.0')
                module_card.description = module.get('description', 'Aucune description')
                
                # Titre du module
                name_label = MDLabel(
                    text=module.get('name', 'Module sans nom'),
                    theme_font_size="Custom",
                    font_size="18sp",
                    size_hint_y=None,
                    height=dp(30)
                )
                
                # Version
                version_label = MDLabel(
                    text=f"Version: {module.get('version', '1.0.0')}",
                    theme_font_size="Custom",
                    font_size="14sp",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(20)
                )
                
                # Description
                description = module.get('description', '')
                if description:
                    desc_label = MDLabel(
                        text=description,
                        theme_font_size="Custom",
                        font_size="14sp",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(20)
                    )
                    module_card.add_widget(desc_label)
                
                # Assembler la carte
                module_card.add_widget(name_label)
                module_card.add_widget(version_label)
                
                # Ajouter un gestionnaire d'événements pour le clic sur la carte
                module_card.bind(on_touch_down=self._on_module_card_touch)
                
                # Ajouter la carte au conteneur
                self.modules_container.add_widget(module_card)
            
            # Vider le conteneur d'écrans
            self.screens_container.clear_widgets()
            
            # Réinitialiser l'écran sélectionné
            self.selected_module = None
            self.selected_screen = None
            self.index_value.text = "Sélectionnez un module et un écran"
        except Exception as e:
            self.logger.error(f"Erreur lors du rafraîchissement des données: {str(e)}")
            
    def _on_module_card_touch(self, card, touch):
        """Gestionnaire d'événements touch pour les cartes de module"""
        if card.collide_point(*touch.pos):
            # Sélectionner le module quand la carte est touchée
            self.select_module(card.id)
            return True
        return False
    
    def select_module(self, module_id):
        """
        Sélectionne un module et affiche ses écrans
        
        Args:
            module_id (str): Identifiant du module
        """
        try:
            self.selected_module = module_id
            
            # Mettre à jour l'interface
            self.ids.screens_title.text = f"Écrans du module: {module_id}"
            
            # Récupérer les écrans du module
            screens = self.discovery.get_module_screens(module_id)
            
            # Vider le conteneur d'écrans
            self.screens_container.clear_widgets()
            
            # Ajouter les cartes d'écrans de façon programmatique
            for screen in screens:
                # Créer la carte
                screen_card = MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(100),
                    padding=dp(10),
                    spacing=dp(4),
                    md_bg_color=[1, 1, 1, 1],
                    elevation=1,
                    radius=dp(8)
                )
                
                # Conserver les informations dans la carte
                screen_card.module_id = module_id
                screen_card.screen_id = screen.get('id', '')
                screen_card.name = screen.get('name', 'Écran sans nom')
                screen_card.description = screen.get('description', 'Aucune description')
                
                # En-tête avec titre et bouton de copie
                header = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(30)
                )
                
                # Titre
                title_label = MDLabel(
                    text=screen.get('name', 'Écran sans nom'),
                    theme_font_size="Custom",
                    font_size="18sp",
                    size_hint_x=0.8
                )
                
                # Bouton de copie
                copy_button = MDIconButton(
                    icon="content-copy",
                    theme_text_color="Hint",
                    size_hint_x=None,
                    width=dp(30)
                )
                
                # Conserver une référence à l'ID pour le callback
                copy_button.module_id = module_id
                copy_button.screen_id = screen.get('id', '')
                copy_button.bind(on_release=self._copy_screen_index)
                
                header.add_widget(title_label)
                header.add_widget(copy_button)
                
                # ID de l'écran
                id_label = MDLabel(
                    text=f"ID: {screen.get('id', '')}",
                    theme_font_size="Custom",
                    font_size="14sp",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(20)
                )
                
                # Description
                desc_label = MDLabel(
                    text=screen.get('description', ''),
                    theme_font_size="Custom",
                    font_size="14sp",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(36)
                )
                
                # Assembler la carte
                screen_card.add_widget(header)
                screen_card.add_widget(id_label)
                screen_card.add_widget(desc_label)
                
                # Ajouter un gestionnaire d'événements pour le clic sur la carte
                screen_card.bind(on_touch_down=self._on_screen_card_touch)
                
                # Ajouter la carte au conteneur
                self.screens_container.add_widget(screen_card)
            
            # Réinitialiser l'écran sélectionné
            self.selected_screen = None
            if self.index_value:
                self.index_value.text = "Sélectionnez un écran"
        except Exception as e:
            self.logger.error(f"Erreur lors de la sélection du module {module_id}: {str(e)}")

    def _on_screen_card_touch(self, card, touch):
        """Gestionnaire d'événements touch pour les cartes d'écran"""
        if card.collide_point(*touch.pos):
            # Sélectionner l'écran quand la carte est touchée
            self.select_screen(card.screen_id)
            return True
        return False
        
    def _copy_screen_index(self, button):
        """Copie l'index d'un écran spécifique"""
        from kivy.core.clipboard import Clipboard
        index = f"{button.module_id}.{button.screen_id}"
        Clipboard.copy(index)
        
        # Afficher une notification
        app = App.get_running_app()
        if hasattr(app, 'show_snackbar'):
            app.show_snackbar(f"Index '{index}' copié")
        else:
            snackbar = MDSnackbar(
                MDSnackbarText(
                    text=f"Index '{index}' copié"
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            snackbar.open()
    
    def select_screen(self, screen_id):
        """
        Sélectionne un écran
        
        Args:
            screen_id (str): Identifiant de l'écran
        """
        if not self.selected_module:
            return
            
        self.selected_screen = screen_id
        
        # Mettre à jour l'index complet
        if self.index_value:
            self.index_value.text = f"{self.selected_module}.{self.selected_screen}"
    
    def copy_index(self, *args):
        """Copie l'index complet dans le presse-papier"""
        if not self.selected_module or not self.selected_screen:
            return
            
        from kivy.core.clipboard import Clipboard
        index = f"{self.selected_module}.{self.selected_screen}"
        Clipboard.copy(index)
        
        # Afficher une notification
        if hasattr(self.app, 'show_snackbar'):
            self.app.show_snackbar(f"Index '{index}' copié")
        else:
            snackbar = MDSnackbar(
                MDSnackbarText(
                    text=f"Index '{index}' copié"
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            snackbar.open()
    
    def go_back(self, *args):
        """Retourne à l'écran précédent"""
        try:
            print("[DEBUG] ModulesAdminScreen.go_back - Début du retour")
            
            # Si l'app a un callback enregistré, l'appeler avec les sélections
            callback_executed = False
            if hasattr(self.app, 'modules_admin_callback'):
                print(f"[DEBUG] ModulesAdminScreen.go_back - modules_admin_callback trouvé: {self.app.modules_admin_callback}")
                if self.app.modules_admin_callback:
                    if self.selected_module and self.selected_screen:
                        print(f"[DEBUG] ModulesAdminScreen.go_back - Exécution du callback avec {self.selected_module}.{self.selected_screen}")
                        try:
                            self.app.modules_admin_callback(self.selected_module, self.selected_screen)
                            callback_executed = True
                            print("[DEBUG] ModulesAdminScreen.go_back - Callback exécuté avec succès")
                        except Exception as e:
                            print(f"[ERROR] ModulesAdminScreen.go_back - Erreur lors de l'exécution du callback: {str(e)}")
                    else:
                        print("[DEBUG] ModulesAdminScreen.go_back - Module ou écran non sélectionné")
            else:
                print("[DEBUG] ModulesAdminScreen.go_back - Pas de callback enregistré")
            
            # Vérifier si le gestionnaire d'écrans existe
            if self.manager is None:
                print("[ERROR] ModulesAdminScreen.go_back - Gestionnaire d'écrans manquant")
                return
            
            # Vérifier si previous_screen existe
            if hasattr(self.app, 'previous_screen') and self.app.previous_screen:
                previous = self.app.previous_screen
                print(f"[DEBUG] ModulesAdminScreen.go_back - Écran précédent trouvé: {previous}")
                
                # Vérifier si l'écran existe dans le gestionnaire
                if previous in self.manager.screen_names:
                    print(f"[DEBUG] ModulesAdminScreen.go_back - Navigation vers {previous}")
                    self.manager.current = previous
                    print("[DEBUG] ModulesAdminScreen.go_back - Navigation réussie")
                else:
                    print(f"[ERROR] ModulesAdminScreen.go_back - Écran {previous} non trouvé dans {self.manager.screen_names}")
                    # Fallback - retour à l'écran par défaut
                    if 'dashboard' in self.manager.screen_names:
                        print("[DEBUG] ModulesAdminScreen.go_back - Retour au dashboard par défaut")
                        self.manager.current = 'dashboard'
            else:
                print("[ERROR] ModulesAdminScreen.go_back - previous_screen non défini")
                # Fallback - retour à l'écran par défaut
                if 'dashboard' in self.manager.screen_names:
                    print("[DEBUG] ModulesAdminScreen.go_back - Retour au dashboard par défaut")
                    self.manager.current = 'dashboard'
        except Exception as e:
            import traceback
            print(f"[ERROR] ModulesAdminScreen.go_back - Exception: {str(e)}")
            traceback.print_exc()
            
            # Tentative désespérée de récupération
            try:
                if self.manager and 'dashboard' in self.manager.screen_names:
                    self.manager.current = 'dashboard'
            except:
                pass


