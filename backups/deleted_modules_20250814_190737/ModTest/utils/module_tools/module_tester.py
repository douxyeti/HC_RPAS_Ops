"""
Testeur de module pour l'architecture modulaire HC_RPAS_Ops
Cet outil lance un environnement isolé pour tester un module sans impacter l'application existante
"""

import os
import sys
import importlib.util
import json
import logging
from typing import Dict, Any, Optional

# Assurez-vous que le chemin racine est dans le PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

# Configuration du logger
logger = logging.getLogger("hc_rpas.module_tester")

class ModuleTester:
    """Classe utilitaire pour tester un module de façon isolée"""
    
    def __init__(self, module_path: str, screen_name: Optional[str] = None):
        self.module_path = os.path.abspath(module_path)
        self.screen_name = screen_name
        self.module_info = {}
        self.screens = []
    
    def validate_module(self) -> bool:
        """Vérifie si le module est valide"""
        # Vérifier si le module existe
        if not os.path.exists(self.module_path):
            logger.error(f"Module introuvable: {self.module_path}")
            return False
        
        # Vérifier si c'est un dossier
        if not os.path.isdir(self.module_path):
            logger.error(f"Le chemin n'est pas un dossier: {self.module_path}")
            return False
        
        # Charger les informations du module si disponibles (support des deux formats)
        # D'abord essayer module_info.json (nouveau format standard)
        info_path = os.path.join(self.module_path, 'module_info.json')
        if not os.path.exists(info_path):
            # Sinon essayer manifest.json (format du module de contrôle des vols)
            info_path = os.path.join(self.module_path, 'manifest.json')
        
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    self.module_info = json.load(f)
                    module_name = self.module_info.get('name', 'Inconnu')
                    logger.info(f"Module info chargé: {module_name}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des infos du module: {str(e)}")
        
        # Identifier les écrans disponibles - chercher d'abord dans screens/ (nouveau format standard)
        screens_dir = os.path.join(self.module_path, 'screens')
        if not os.path.exists(screens_dir) or not os.path.isdir(screens_dir):
            # Sinon chercher dans views/screens/ (format du module de contrôle des vols)
            screens_dir = os.path.join(self.module_path, 'views', 'screens')
        
        if os.path.exists(screens_dir) and os.path.isdir(screens_dir):
            for file in os.listdir(screens_dir):
                if file.endswith('_screen.py'):
                    screen_name = file.replace('_screen.py', '')
                    screen_path = os.path.join(screens_dir, file)
                    screen_class_name = ''.join(word.capitalize() for word in screen_name.split('_')) + 'Screen'
                    
                    self.screens.append({
                        'name': screen_name,
                        'path': screen_path,
                        'class_name': screen_class_name
                    })
            
            logger.info(f"{len(self.screens)} écrans trouvés dans le module")
        else:
            logger.warning(f"Aucun répertoire d'écrans trouvé dans {self.module_path}")
        
        # Si nous n'avons pas trouvé d'écrans mais que le manifest.json contient des écrans, les utiliser
        if not self.screens and 'screens' in self.module_info:
            for screen_info in self.module_info['screens']:
                screen_name = screen_info.get('id', '')
                screen_class_name = screen_info.get('class', '')
                
                # Vérifier si nous pouvons trouver le fichier de l'écran
                potential_paths = [
                    os.path.join(self.module_path, 'views', 'screens', f"{screen_name}_screen.py"),
                    os.path.join(self.module_path, 'screens', f"{screen_name}_screen.py")
                ]
                
                screen_path = None
                for path in potential_paths:
                    if os.path.exists(path):
                        screen_path = path
                        break
                
                if screen_path:
                    self.screens.append({
                        'name': screen_name,
                        'path': screen_path,
                        'class_name': screen_class_name
                    })
                    logger.info(f"Écran trouvé via manifest: {screen_name}")
        
        return True
    
    def get_screen_info(self, screen_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Trouve les informations d'un écran spécifique"""
        target_screen = screen_name or self.screen_name
        
        # Si un écran spécifique est demandé
        if target_screen:
            for screen in self.screens:
                if screen['name'] == target_screen:
                    return screen
            
            logger.error(f"Écran '{target_screen}' introuvable dans le module")
            return None
        
        # Sinon, prendre le premier écran disponible
        if self.screens:
            logger.info(f"Utilisation de l'écran par défaut: {self.screens[0]['name']}")
            return self.screens[0]
        
        logger.error("Aucun écran disponible dans le module")
        return None
    
    def try_load_screen_class(self, screen_info: Dict[str, Any]):
        """Tente de charger la classe d'écran spécifiée"""
        try:
            logger.info(f"Chargement de l'écran: {screen_info['path']}")
            spec = importlib.util.spec_from_file_location("screen_module", screen_info['path'])
            screen_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(screen_module)
            
            screen_class = getattr(screen_module, screen_info['class_name'], None)
            if not screen_class:
                logger.error(f"Classe d'écran introuvable: {screen_info['class_name']}")
                return None
            
            return screen_class
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Erreur lors du chargement de l'écran: {str(e)}")
            logger.debug(error_details)
            return None

    def launch_module_app(self):
        """Lance une application Kivy minimale pour tester le module"""
        try:
            # Importer les classes Kivy seulement si nécessaire, pour éviter les dépendances
            from kivy.app import App
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.screenmanager import ScreenManager
            from kivymd.app import MDApp
            
            class TestModuleApp(MDApp):
                def __init__(self, tester, **kwargs):
                    super().__init__(**kwargs)
                    self.tester = tester
                    self.title = f"Module Tester - {os.path.basename(tester.module_path)}"
                
                def build(self):
                    # Valider le module
                    if not self.tester.validate_module():
                        return self._build_error_view("Module invalide")
                    
                    # Obtenir les informations de l'écran
                    screen_info = self.tester.get_screen_info()
                    if not screen_info:
                        return self._build_error_view("Aucun écran disponible")
                    
                    # Charger la classe de l'écran
                    screen_class = self.tester.try_load_screen_class(screen_info)
                    if not screen_class:
                        return self._build_error_view(f"Impossible de charger l'écran {screen_info['name']}")
                    
                    try:
                        # Créer une instance de l'écran
                        screen = screen_class()
                        
                        # Créer un gestionnaire d'écrans pour l'afficher
                        sm = ScreenManager()
                        sm.add_widget(screen)
                        
                        return sm
                    except Exception as e:
                        import traceback
                        error_details = traceback.format_exc()
                        return self._build_error_view(f"Erreur lors de l'instanciation de l'écran: {str(e)}\n\n{error_details}")
                
                def _build_error_view(self, message):
                    """Construit une vue d'erreur"""
                    layout = BoxLayout(orientation='vertical', padding=20)
                    layout.add_widget(Label(
                        text="ERREUR DU TESTEUR DE MODULE",
                        size_hint_y=None,
                        height=50,
                        font_size=24
                    ))
                    layout.add_widget(Label(
                        text=message,
                        halign='left',
                        valign='top',
                        text_size=(800, None),
                        size_hint_y=None,
                        height=400
                    ))
                    return layout
            
            # Lancer l'application de test
            TestModuleApp(self).run()
            
        except ImportError as e:
            logger.error(f"Impossible d'importer les dépendances Kivy: {str(e)}")
            logger.error("Vérifiez que Kivy et KivyMD sont installés et accessibles")
            return False
        
        return True

def print_usage():
    print("Usage: python module_tester.py <chemin_module> [nom_écran]")
    print("Exemple: python module_tester.py app/modules_new/operations main")
    print("\nOptions:")
    print("  --list-screens    Liste les écrans disponibles dans le module sans le lancer")
    print("  --info            Affiche les informations du module sans le lancer")

if __name__ == "__main__":
    import argparse
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Parsing des arguments
    parser = argparse.ArgumentParser(description="Testeur de module pour HC_RPAS_Ops")
    parser.add_argument("module_path", help="Chemin vers le module à tester")
    parser.add_argument("screen_name", nargs="?", help="Nom de l'écran à charger (optionnel)")
    parser.add_argument("--list-screens", action="store_true", help="Liste les écrans disponibles")
    parser.add_argument("--info", action="store_true", help="Affiche les informations du module")
    args = parser.parse_args()
    
    tester = ModuleTester(args.module_path, args.screen_name)
    
    if args.list_screens:
        if tester.validate_module():
            print("\nÉcrans disponibles:")
            for i, screen in enumerate(tester.screens, 1):
                print(f"{i}. {screen['name']} ({screen['class_name']})")
        sys.exit(0)
    
    if args.info:
        if tester.validate_module():
            print("\nInformations du module:")
            for key, value in tester.module_info.items():
                if isinstance(value, (list, dict)):
                    print(f"{key}: {json.dumps(value, indent=2)}")
                else:
                    print(f"{key}: {value}")
        sys.exit(0)
    
    # Lancer l'application de test
    tester.launch_module_app()
