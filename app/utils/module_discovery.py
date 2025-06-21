"""
Utilitaire pour découvrir et interagir avec les modules installés dans l'application.
Permet de récupérer la liste des modules et leurs écrans indexés dans Firebase.
"""
from typing import Dict, List, Any, Optional
import importlib
import os
import logging
from pathlib import Path

class ModuleDiscovery:
    """Utilitaire pour découvrir et interagir avec les modules installés"""
    
    def __init__(self, firebase_service):
        """
        Initialise l'utilitaire de découverte de modules
        
        Args:
            firebase_service: Instance du service Firebase
        """
        self.firebase_service = firebase_service
        self.modules_cache = {}
        self.screens_cache = {}
        self.logger = logging.getLogger('hc_rpas.module_discovery')
        
        # Détecter la branche Git courante
        self.branch_name = self._get_git_branch()
        self.logger.info(f"ModuleDiscovery initialisé pour la branche: '{self.branch_name}'")
    
    def _get_git_branch(self) -> str:
        """
        Récupère le nom de la branche Git courante
        
        Returns:
            str: Nom de la branche Git courante
        """
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            branch = result.stdout.strip()
            self.logger.info(f"Branche Git détectée: {branch}")
            return branch
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection de la branche Git: {e}")
            return ""
    
    def _get_known_branches(self) -> List[str]:
        """
        Récupère la liste des branches Git connues sans utiliser get_collections
        
        Returns:
            List[str]: Liste des noms de branches Git connues
        """
        try:
            import subprocess
            # Récupérer toutes les branches Git locales et distantes
            result = subprocess.run(
                ['git', 'branch', '-a'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Impossible de récupérer les branches Git: {result.stderr}")
                return [self.branch_name] if self.branch_name else []
            
            # Extraire les noms de branches
            branches = []
            for line in result.stdout.splitlines():
                # Nettoyer la ligne et extraire le nom de la branche
                branch = line.strip()
                if branch.startswith('*'):  # Branche courante
                    branch = branch[1:].strip()
                if branch.startswith('remotes/'):  # Branche distante
                    branch = branch.split('/', 2)[-1]
                
                # Filtrer les branches inutiles comme HEAD, etc.
                if branch and not branch.endswith('/HEAD') and branch != 'HEAD':
                    branches.append(branch)
            
            # Ajouter la branche courante si elle n'est pas déjà présente
            if self.branch_name and self.branch_name not in branches:
                branches.append(self.branch_name)
            
            self.logger.debug(f"Branches Git connues: {branches}")
            return list(set(branches))  # Éliminer les doublons
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des branches Git: {str(e)}")
            return [self.branch_name] if self.branch_name else []
    
    def _sanitize_branch_name(self, branch_name: str) -> str:
        """
        Nettoie le nom de la branche pour éviter les caractères problématiques dans Firebase
        
        Args:
            branch_name (str): Nom de la branche Git
            
        Returns:
            str: Nom de branche nettoyé pour Firebase
        """
        if not branch_name:
            return ""
            
        # Remplacer les caractères spéciaux par des équivalents compatibles avec Firebase
        # Firebase n'accepte pas les '/' dans les chemins de collection
        sanitized = branch_name.replace('/', '_SLASH_').replace('.', '_DOT_').replace('#', '_HASH_')
        sanitized = sanitized.replace('$', '_DOLLAR_').replace('[', '_LBRACKET_').replace(']', '_RBRACKET_')
        
        return sanitized
    
    def _unsanitize_branch_name(self, sanitized_branch: str) -> str:
        """
        Retrouve le nom de branche original à partir de la version nettoyée
        
        Args:
            sanitized_branch (str): Nom de branche nettoyé pour Firebase
            
        Returns:
            str: Nom de branche original
        """
        if not sanitized_branch:
            return ""
            
        # Reconvertir les marqueurs en caractères spéciaux
        original = sanitized_branch.replace('_SLASH_', '/').replace('_DOT_', '.').replace('_HASH_', '#')
        original = original.replace('_DOLLAR_', '$').replace('_LBRACKET_', '[').replace('_RBRACKET_', ']')
        
        return original
    
    def _extract_branch_name(self, collection_name: str, prefix="module_indexes_modules_") -> str:
        """
        Extrait le nom de la branche à partir du nom de la collection
        
        Args:
            collection_name (str): Nom de la collection
            prefix (str): Préfixe à retirer
            
        Returns:
            str: Nom de la branche extrait
        """
        if collection_name.startswith(prefix):
            sanitized_branch = collection_name[len(prefix):]
            return self._unsanitize_branch_name(sanitized_branch)
        return ""
    
    def get_installed_modules(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des modules installés depuis Firebase pour toutes les branches connues.
        Commence par la branche Git courante, puis vérifie les autres branches connues.
        
        Returns:
            List[Dict[str, Any]]: Liste des modules installés
        """
        try:
            self.logger.info(f"Branche Git détectée: {self.branch_name}")
            self.logger.info(f"ModuleDiscovery initialisé pour la branche: '{self.branch_name}'")
            
            # Vérifier si les modules sont déjà en cache
            if self.modules_cache:
                return list(self.modules_cache.values())
                
            modules_list = []
            modules_found_in_branches = False
            
            # D'abord traiter la branche courante (priorité)
            sanitized_branch = self._sanitize_branch_name(self.branch_name)
            branch_collection = f"module_indexes_modules_{sanitized_branch}"
            self.logger.info(f"Récupération des modules depuis la collection de la branche courante: {branch_collection}")
            
            branch_modules = self.firebase_service.get_collection(branch_collection)
            
            if branch_modules:
                modules_found_in_branches = True
                # Ajouter le champ branch à chaque module
                for module in branch_modules:
                    module["branch"] = self.branch_name
                    
                # Ajouter ces modules à la liste finale
                modules_list.extend(branch_modules)
                self.logger.info(f"Trouvé {len(branch_modules)} modules dans la branche courante")
            
            # Ensuite, récupérer les modules des autres branches connues
            known_branches = self._get_known_branches()
            self.logger.info(f"Branches Git connues: {known_branches}")
            
            # Exclure la branche courante déjà traitée
            if self.branch_name in known_branches:
                known_branches.remove(self.branch_name)
                
            for branch_name in known_branches:
                if not branch_name:  # Ignorer les branches sans nom
                    continue
                    
                sanitized_name = self._sanitize_branch_name(branch_name)
                collection_name = f"module_indexes_modules_{sanitized_name}"
                self.logger.info(f"Vérification des modules dans la branche: {branch_name} (collection: {collection_name})")
                
                branch_modules = self.firebase_service.get_collection(collection_name)
                
                # Ajouter les informations de branche à chaque module
                for module in branch_modules:
                    if 'id' in module:
                        module['branch'] = branch_name
                        self.logger.debug(f"Module trouvé dans la branche {branch_name}: {module['id']}")
                
                modules_list.extend(branch_modules)
            
            # Mettre en cache - utiliser l'ID et la branche comme clé unique pour éviter les doublons
            self.modules_cache = {}
            for module in modules_list:
                if 'id' in module and 'branch' in module:
                    key = f"{module['id']}_{module['branch']}"
                    self.modules_cache[key] = module
            
            self.logger.info(f"Nombre total de modules trouvés: {len(modules_list)}")
            return modules_list
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des modules: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def get_module_screens(self, module_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les écrans d'un module spécifique depuis toutes les branches connues
        
        Args:
            module_id (str): Identifiant du module
            
        Returns:
            List[Dict[str, Any]]: Liste des écrans du module dans toutes les branches
        """
        try:
            # Vérifier si déjà en cache
            if module_id in self.screens_cache and self.screens_cache[module_id]:
                return list(self.screens_cache[module_id].values())
            
            screens_list = []
            
            # D'abord récupérer les écrans de la branche courante (priorité)
            sanitized_branch = self._sanitize_branch_name(self.branch_name) if self.branch_name else ""
            current_branch_collection = f"module_indexes_screens_{module_id}_{sanitized_branch}" if sanitized_branch else f"module_indexes_screens_{module_id}"
            self.logger.info(f"Récupération des écrans pour le module {module_id} dans la branche courante: {current_branch_collection}")
            
            current_branch_screens = self.firebase_service.get_collection(current_branch_collection)
            
            # Ajouter des informations sur la provenance
            for screen in current_branch_screens:
                if 'id' in screen:
                    screen['branch'] = self.branch_name
                    self.logger.debug(f"Écran trouvé dans la branche courante {self.branch_name}: {screen['id']}")
            
            screens_list.extend(current_branch_screens)
            
            # Ensuite récupérer les écrans des autres branches connues
            known_branches = self._get_known_branches()
            self.logger.info(f"Branches Git connues pour la recherche d'écrans: {known_branches}")
            
            # Exclure la branche courante déjà traitée
            if self.branch_name in known_branches:
                known_branches.remove(self.branch_name)
            
            # Format des collections d'écrans: module_indexes_screens_{module_id}_{branch_name}
            for branch_name in known_branches:
                if not branch_name:  # Ignorer les branches sans nom
                    continue
                    
                sanitized_name = self._sanitize_branch_name(branch_name)
                collection_name = f"module_indexes_screens_{module_id}_{sanitized_name}"
                self.logger.info(f"Vérification des écrans du module {module_id} dans la branche: {branch_name} (collection: {collection_name})")
                
                branch_screens = self.firebase_service.get_collection(collection_name)
                
                # Ajouter des informations sur la provenance
                for screen in branch_screens:
                    if 'id' in screen:
                        screen['branch'] = branch_name
                        self.logger.debug(f"Écran trouvé dans la branche {branch_name}: {screen['id']}")
                
                screens_list.extend(branch_screens)
            
            # Détails de tous les écrans pour le débogage
            self.logger.info(f"Nombre total d'écrans récupérés pour le module {module_id}: {len(screens_list)}")
            if screens_list:
                for idx, screen in enumerate(screens_list):
                    self.logger.debug(f"Écran {idx+1}: ID={screen.get('id', 'N/A')}, Nom={screen.get('name', 'N/A')}, Branche={screen.get('branch', 'N/A')}")
            
            # Mettre en cache - utiliser l'ID et la branche comme clé unique pour éviter les doublons
            if module_id not in self.screens_cache:
                self.screens_cache[module_id] = {}
            
            for screen in screens_list:
                if 'id' in screen and 'branch' in screen:
                    key = f"{screen['id']}_{screen['branch']}"
                    self.screens_cache[module_id][key] = screen
            
            return list(self.screens_cache[module_id].values())
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des écrans du module {module_id} pour la branche {self.branch_name}: {str(e)}")
            return []
    
    def get_screen_details(self, module_id: str, screen_id: str, branch_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'un écran spécifique depuis n'importe quelle branche
        
        Args:
            module_id (str): Identifiant du module
            screen_id (str): Identifiant de l'écran
            branch_name (str, optional): Nom de la branche spécifique. Par défaut, None (utilise la branche courante)
            
        Returns:
            Optional[Dict[str, Any]]: Détails de l'écran ou None si non trouvé
        """
        try:
            # Vérifier le cache d'abord
            cache_key = f"{module_id}_{screen_id}_{branch_name if branch_name else self.branch_name}"
            if cache_key in self.screens_cache.get('details', {}):
                self.logger.debug(f"Détails de l'écran {screen_id} du module {module_id} trouvés dans le cache")
                return self.screens_cache['details'][cache_key]
            
            # Si on a fourni une branche spécifique, chercher uniquement dans cette branche
            if branch_name:
                sanitized_name = self._sanitize_branch_name(branch_name)
                collection_name = f"module_indexes_screens_{module_id}_{sanitized_name}"
                self.logger.info(f"Récupération des détails de l'écran {screen_id} du module {module_id} depuis la branche: {branch_name}")
                
                # Récupérer tous les écrans du module dans cette branche
                screens = self.firebase_service.get_collection(collection_name)
                
                for screen in screens:
                    if screen.get('id') == screen_id:
                        # Marquer la branche d'origine
                        screen['branch'] = branch_name
                        
                        # Mettre en cache
                        if 'details' not in self.screens_cache:
                            self.screens_cache['details'] = {}
                        self.screens_cache['details'][cache_key] = screen
                        
                        self.logger.debug(f"Détails de l'écran {screen_id} trouvés dans la branche {branch_name}")
                        return screen
                
                self.logger.warning(f"\u00c9cran {screen_id} non trouvé dans la branche {branch_name}")
                return None
            
            # Sinon, commencer par la branche courante puis chercher dans les autres branches
            # Branche courante d'abord
            sanitized_branch = self._sanitize_branch_name(self.branch_name) if self.branch_name else ""
            current_branch_collection = f"module_indexes_screens_{module_id}_{sanitized_branch}" if sanitized_branch else f"module_indexes_screens_{module_id}"
            self.logger.info(f"Récupération des détails de l'écran {screen_id} du module {module_id} dans la branche courante: {current_branch_collection}")
            
            current_branch_screens = self.firebase_service.get_collection(current_branch_collection)
            
            for screen in current_branch_screens:
                if screen.get('id') == screen_id:
                    # Marquer la branche d'origine
                    screen['branch'] = self.branch_name
                    
                    # Mettre en cache
                    if 'details' not in self.screens_cache:
                        self.screens_cache['details'] = {}
                    self.screens_cache['details'][cache_key] = screen
                    
                    self.logger.debug(f"Détails de l'écran {screen_id} trouvés dans la branche courante {self.branch_name}")
                    return screen
            
            # Ensuite, chercher dans les autres branches connues
            known_branches = self._get_known_branches()
            # Exclure la branche courante déjà traitée
            if self.branch_name in known_branches:
                known_branches.remove(self.branch_name)
                
            self.logger.info(f"Recherche de l'écran {screen_id} dans les autres branches connues: {known_branches}")
            
            for branch in known_branches:
                if not branch:  # Ignorer les branches sans nom
                    continue
                    
                sanitized_name = self._sanitize_branch_name(branch)
                collection_name = f"module_indexes_screens_{module_id}_{sanitized_name}"
                self.logger.info(f"Recherche de l'écran {screen_id} dans la collection: {collection_name}")
                
                branch_screens = self.firebase_service.get_collection(collection_name)
                
                for screen in branch_screens:
                    if screen.get('id') == screen_id:
                        # Marquer la branche d'origine
                        screen['branch'] = branch
                        
                        # Mettre en cache
                        if 'details' not in self.screens_cache:
                            self.screens_cache['details'] = {}
                        self.screens_cache['details'][cache_key] = screen
                        
                        self.logger.debug(f"Détails de l'écran {screen_id} trouvés dans la branche {branch}")
                        return screen
                        
            self.logger.warning(f"\u00c9cran {screen_id} non trouvé dans aucune branche")
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des détails de l'écran {screen_id} du module {module_id}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _discover_modules_from_filesystem(self) -> List[Dict[str, Any]]:
        """
        Découvre les modules installés en parcourant le système de fichiers
        
        Returns:
            List[Dict[str, Any]]: Liste des modules découverts
        """
        modules = []
        services_dir = Path("services")
        
        if not services_dir.exists():
            return []
            
        # Chercher tous les répertoires commençant par "module_"
        for module_dir in services_dir.glob("module_*"):
            if not module_dir.is_dir():
                continue
                
            manifest_path = module_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    import json
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        
                    module_id = manifest.get('module_id') or module_dir.name.replace('module_', '')
                    modules.append({
                        'id': module_id,
                        'name': manifest.get('name', module_id),
                        'version': manifest.get('version', '1.0.0'),
                        'description': manifest.get('description', '')
                    })
                except Exception as e:
                    self.logger.error(f"Erreur lors de la lecture du manifest {manifest_path}: {str(e)}")
        
        return modules
        
    def navigate_to_module_screen(self, app_instance, module_id: str, screen_id: str, 
                                field_id: Optional[str] = None, **kwargs):
        """
        Navigue vers un écran spécifique d'un module
        
        Args:
            app_instance: Instance de l'application Kivy
            module_id (str): Identifiant du module
            screen_id (str): Identifiant de l'écran
            field_id (Optional[str]): Identifiant du champ (optionnel)
            **kwargs: Arguments supplémentaires à passer à l'écran
        
        Returns:
            bool: True si la navigation a réussi, False sinon
        """
        try:
            # Construire le chemin du module
            module_path = f"services.module_{module_id}"
            
            # Tenter d'importer le module
            try:
                module = importlib.import_module(module_path)
                # Vérifier si le module a un registre
                if hasattr(module, 'get_registry'):
                    registry = module.get_registry()
                    # Naviguer vers l'écran
                    return registry.navigate_to_screen(
                        screen_id=screen_id,
                        field_id=field_id,
                        app=app_instance,
                        **kwargs
                    )
                else:
                    self.logger.error(f"Le module {module_id} n'a pas de méthode get_registry")
            except ImportError as e:
                self.logger.error(f"Impossible d'importer le module {module_path}: {str(e)}")
            
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la navigation vers l'écran {module_id}.{screen_id}: {str(e)}")
            return False
