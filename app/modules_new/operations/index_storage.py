"""
Système de stockage des index dans Firebase pour le module de contrôle des vols.
Permet une synchronisation multi-utilisateurs des index.
Inclut le nom de la branche pour différencier les applications.
"""

import json
import logging
import subprocess
from typing import Dict, List, Any, Optional

class FirebaseIndexStorage:
    """
    Gestionnaire de stockage des index pour les modules dans Firebase.
    Permet un accès multi-utilisateurs synchronisé aux index des écrans.
    """
    
    COLLECTION_NAME = "module_indexes"
    
    def __init__(self, firebase_service):
        """
        Initialise le stockage des index avec le service Firebase existant
        
        Args:
            firebase_service: Instance du service Firebase déjà configuré
        """
        self.firebase = firebase_service
        self.logger = logging.getLogger('hc_rpas.index_storage')
        self.branch_name = self._get_clean_branch_name()
        
    def _get_clean_branch_name(self) -> str:
        """
        Récupère le nom de la branche Git actuelle et enlève le préfixe 'dev_' si présent
        
        Returns:
            Nom nettoyé de la branche
        """
        try:
            # Récupérer le nom de la branche Git
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                   capture_output=True, text=True, check=True)
            branch_name = result.stdout.strip()
            
            # Enlever le préfixe 'dev_' si présent
            if branch_name.startswith('dev_'):
                branch_name = branch_name[4:]
                
            self.logger.info(f"Nom de branche détecté pour l'indexation: {branch_name}")
            return branch_name
        except Exception as e:
            self.logger.warning(f"Impossible de détecter le nom de la branche: {str(e)}")
            return "default_app"
    
    def register_module(self, module_id: str, module_data: Dict[str, Any]) -> bool:
        """
        Enregistre les métadonnées d'un module
        
        Args:
            module_id: Identifiant unique du module
            module_data: Données du module (nom, version, description...)
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            # Ajouter le nom de la branche/application aux métadonnées
            module_data['application_name'] = self.branch_name
            
            collection_name = f"{self.COLLECTION_NAME}_modules_{self.branch_name}"
            result = self.firebase.add_document_with_id(collection_name, module_id, module_data)
            self.logger.info(f"Module '{module_id}' enregistré dans Firebase")
            return result
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement du module '{module_id}': {str(e)}")
            return False
        
    def register_screen(self, module_id: str, screen_id: str, screen_data: Dict[str, Any]) -> bool:
        """
        Enregistre un écran avec ses champs indexés
        
        Args:
            module_id: Identifiant du module
            screen_id: Identifiant de l'écran
            screen_data: Données de l'écran et ses champs
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            # Adapter le format aux collections/documents de Firestore
            collection_name = f"{self.COLLECTION_NAME}_screens_{module_id}_{self.branch_name}"
            document_id = screen_id
            
            # Ajouter l'identifiant du module et de l'application aux données pour les requêtes
            screen_data['module_id'] = module_id
            screen_data['application_name'] = self.branch_name
            
            # Utiliser la méthode existante pour ajouter le document
            result = self.firebase.add_document_with_id(collection_name, document_id, screen_data)
            self.logger.info(f"Écran '{module_id}.{screen_id}' enregistré dans Firebase")
            return result
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de l'écran '{module_id}.{screen_id}': {str(e)}")
            return False
    
    def get_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les métadonnées d'un module
        
        Args:
            module_id: Identifiant du module
            
        Returns:
            Données du module ou None si non trouvé
        """
        try:
            collection_name = f"{self.COLLECTION_NAME}_modules_{self.branch_name}"
            return self.firebase.get_document(collection_name, module_id)
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du module '{module_id}': {str(e)}")
            return None
    
    def get_screen(self, module_id: str, screen_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'un écran indexé
        
        Args:
            module_id: Identifiant du module
            screen_id: Identifiant de l'écran
            
        Returns:
            Données de l'écran ou None si non trouvé
        """
        try:
            collection_name = f"{self.COLLECTION_NAME}_screens_{module_id}_{self.branch_name}"
            return self.firebase.get_document(collection_name, screen_id)
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de l'écran '{module_id}.{screen_id}': {str(e)}")
            return None
    
    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère tous les modules enregistrés
        
        Returns:
            Dictionnaire de modules {module_id: module_data}
        """
        try:
            collection_name = f"{self.COLLECTION_NAME}_modules_{self.branch_name}"
            documents = self.firebase.get_collection(collection_name)
            
            # Convertir la liste en dictionnaire avec module_id comme clé
            modules_dict = {}
            for module_data in documents:
                if 'id' in module_data:
                    modules_dict[module_data['id']] = module_data
                    
            return modules_dict
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des modules: {str(e)}")
            return {}
    
    def get_all_screens(self, module_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Récupère tous les écrans, filtré par module si spécifié
        
        Args:
            module_id: Identifiant du module (optionnel)
            
        Returns:
            Dictionnaire d'écrans {screen_id: screen_data} ou {module_id.screen_id: screen_data}
        """
        try:
            results = {}
            
            if module_id:
                # Construire le nom de collection incluant l'ID du module et le nom de l'application
                collection_name = f"{self.COLLECTION_NAME}_screens_{module_id}_{self.branch_name}"
                documents = self.firebase.get_collection(collection_name)
                
                # Convertir la liste en dictionnaire
                screens_dict = {}
                for screen_data in documents:
                    if 'id' in screen_data:
                        screens_dict[screen_data['id']] = screen_data
                    
                return screens_dict
            else:
                # Pour récupérer tous les écrans de tous les modules,
                # nous devons d'abord récupérer tous les modules
                modules_dict = self.get_all_modules()
                
                # Pour chaque module, récupérer ses écrans
                for module_id in modules_dict.keys():
                    module_screens = self.get_all_screens(module_id)
                    for screen_id, screen_data in module_screens.items():
                        # Créer une clé composée pour l'identificateur complet
                        results[f"{module_id}.{screen_id}"] = screen_data
                
                return results
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des écrans: {str(e)}")
            return {}
    
    def register_from_manifest(self, module_id: str, manifest_data: Dict[str, Any]) -> bool:
        """
        Enregistre un module et tous ses écrans à partir d'un manifest
        
        Args:
            module_id: Identifiant du module
            manifest_data: Données du manifest (contenant module_info et screens)
            
        Returns:
            True si l'enregistrement a réussi, False sinon
        """
        try:
            # Enregistrer le module
            module_info = {
                "id": module_id,
                "name": manifest_data.get("name", module_id),
                "version": manifest_data.get("version", "1.0.0"),
                "description": manifest_data.get("description", ""),
                "main_screen": manifest_data.get("main_screen", ""),
                "updated_at": int(__import__("time").time())
            }
            self.register_module(module_id, module_info)
            
            # Enregistrer les écrans
            screens = manifest_data.get("screens", [])
            success_count = 0
            for screen in screens:
                screen_id = screen.get("id")
                if screen_id:
                    # Ajouter timestamp et identifiant pour la référence
                    screen["updated_at"] = int(__import__("time").time())
                    screen["id"] = screen_id  # S'assurer que l'ID est dans les données
                    
                    # Enregistrer l'écran
                    if self.register_screen(module_id, screen_id, screen):
                        success_count += 1
            
            self.logger.info(f"Module '{module_id}' et {success_count}/{len(screens)} écrans enregistrés dans Firebase")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement du manifest '{module_id}': {str(e)}")
            return False
