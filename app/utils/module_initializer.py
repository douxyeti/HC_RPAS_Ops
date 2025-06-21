#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module d'initialisation automatique pour les modules satellites
Ce module vérifie si un index existe pour la branche courante et en crée un si nécessaire
"""

import os
import sys
import subprocess
import importlib.util
import logging
import time
import re
import datetime
from typing import Optional, List, Dict, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('hc_rpas.module_initializer')

class ModuleInitializer:
    """
    Classe responsable de l'initialisation des modules au démarrage
    - Vérifie si un index existe pour la branche courante
    - Crée un index si nécessaire
    - Configure le module pour être visible dans l'écosystème
    """
    
    def __init__(self):
        """Initialisation"""
        self.current_branch = self._get_current_branch()
        self.firebase_service = None
        self.module_indexed = False
        
        logger.info(f"Initialisation du module pour la branche: {self.current_branch}")
    
    def _get_current_branch(self) -> str:
        """Récupère le nom de la branche Git courante"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'], 
                capture_output=True, 
                text=True,
                check=True
            )
            branch_name = result.stdout.strip()
            return branch_name if branch_name else "unknown"
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la branche Git: {e}")
            return "unknown"
    
    def _sanitize_branch_name(self, branch_name: str) -> str:
        """
        Nettoie le nom de branche pour Firebase (remplace les caractères non valides)
        Firebase n'accepte pas certains caractères comme '/', '.' dans les noms de collection
        """
        if not branch_name:
            return "unknown"
        
        # Remplace les caractères problématiques
        sanitized = branch_name.replace('/', '_SLASH_')
        sanitized = sanitized.replace('.', '_DOT_')
        sanitized = sanitized.replace('#', '_HASH_')
        sanitized = sanitized.replace('$', '_DOLLAR_')
        sanitized = sanitized.replace('[', '_LBRACKET_')
        sanitized = sanitized.replace(']', '_RBRACKET_')
        sanitized = sanitized.replace('*', '_STAR_')
        return sanitized
    
    def initialize_with_services(self, firebase_service):
        """
        Initialise le module avec les services requis
        Cette méthode doit être appelée après l'initialisation des services de l'application
        """
        self.firebase_service = firebase_service
        
        # Vérifier si l'indexation est nécessaire
        if self._is_indexing_needed():
            logger.info(f"L'index n'existe pas pour la branche {self.current_branch}. Lancement de l'indexation...")
            self._run_indexing()
        else:
            logger.info(f"L'index existe déjà pour la branche {self.current_branch}. Pas besoin d'indexer.")
            self.module_indexed = True
    
    def _is_indexing_needed(self) -> bool:
        """
        Vérifie si l'indexation est nécessaire pour la branche courante dans plusieurs cas :
        1. Si la collection d'index n'existe pas ou est vide
        2. Si la branche est en mode développement (contient 'dev_' ou 'develop')
        3. Si le nombre d'écrans dans le code source diffère du nombre dans l'index
        """
        if not self.firebase_service:
            return False
        
        sanitized_branch = self._sanitize_branch_name(self.current_branch)
        collection_name = f"app_screens_index_{sanitized_branch}"
        
        # Vérifier si la collection existe et n'est pas vide
        results = self.firebase_service.get_collection(collection_name)
        if not results or len(results) == 0:
            logger.info(f"Indexation nécessaire: Collection {collection_name} vide ou inexistante")
            return True
        
        # Vérifier si c'est une branche de développement
        is_dev_branch = 'dev_' in self.current_branch.lower() or 'develop' in self.current_branch.lower()
        
        # Si c'est une branche de développement, on vérifie si les écrans ont changé
        if is_dev_branch:
            # Trouver les écrans potentiels dans le code source
            potential_screens_count = self._count_potential_screens()
            
            # Récupérer le nombre d'écrans dans l'index
            indexed_screens_count = 0
            metadata_doc = None
            
            # Chercher le document de métadonnées qui contient le nombre d'écrans indexés
            for doc in results:
                if doc.get('id') == 'app_screens_index':
                    metadata_doc = doc
                    indexed_screens_count = doc.get('screen_count', 0)
                    break
            
            # Si le nombre diffère ou si les métadonnées sont absentes, réindexer
            if not metadata_doc or potential_screens_count > indexed_screens_count:
                logger.info(f"Indexation nécessaire: Branche de développement avec des changements détectés. "
                            f"Écrans trouvés: {potential_screens_count}, Écrans indexés: {indexed_screens_count}")
                return True
                
            # Si la dernière indexation date de plus d'une heure, réindexer (pour les branches dev)
            if metadata_doc and 'created_at' in metadata_doc:
                try:
                    last_indexed_time = datetime.datetime.fromisoformat(metadata_doc['created_at'])
                    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
                    
                    if last_indexed_time < one_hour_ago:
                        logger.info(f"Indexation nécessaire: Dernière indexation trop ancienne "
                                   f"({last_indexed_time.isoformat()})")
                        return True
                except (ValueError, TypeError):
                    pass  # Ignorer les erreurs de parsing de date
        
        # Si aucune condition n'est remplie, pas besoin de réindexer
        logger.info(f"Indexation non nécessaire: Collection {collection_name} existe et est à jour")
        return False
        
    def _count_potential_screens(self) -> int:
        """
        Compte le nombre d'écrans potentiels dans le code source
        """
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screen_count = 0
        
        # Trouver tous les fichiers Python qui pourraient contenir des écrans
        for root, _, files in os.walk(os.path.join(app_dir, "app")):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    # Vérifier si le fichier pourrait contenir un écran
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            # Compter les classes potentielles d'écran
                            screens = re.findall(r"class\s+(\w+)(?:Screen|Window|View|Page)?\s*\(", content)
                            for class_name in screens:
                                if ("Screen" in class_name or 
                                    "Window" in class_name or 
                                    "View" in class_name or 
                                    "Page" in class_name or
                                    "screen" in content.lower()):
                                    screen_count += 1
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
                    
        return screen_count
    
    def _run_indexing(self) -> bool:
        """
        Exécute l'indexation des écrans et la création du module directement (sans scripts externes)
        Retourne True en cas de succès
        """
        try:
            # Indexer les écrans de l'application
            logger.info(f"Démarrage de l'indexation des écrans pour la branche: {self.current_branch}")
            indexed_screens = self._index_screens()
            
            if not indexed_screens or len(indexed_screens) == 0:
                logger.error("Aucun écran n'a été indexé. Abandon.")
                return False
                
            logger.info(f"Indexation réussie: {len(indexed_screens)} écrans trouvés")
            
            # Créer le module dans Firebase
            result = self._create_module(indexed_screens)
            
            if not result:
                logger.error("Échec de la création du module. Abandon.")
                return False
                
            logger.info("Création du module réussie")
            self.module_indexed = True
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation et création du module: {e}")
            return False
            
    def _index_screens(self) -> list:
        """
        Indexe tous les écrans de l'application
        Retourne la liste des écrans indexés
        """
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        screens = []
        
        # Sanitize la branche pour le nom de collection
        sanitized_branch = self._sanitize_branch_name(self.current_branch)
        collection_name = f"app_screens_index_{sanitized_branch}"
        
        # Trouver tous les fichiers Python qui pourraient contenir des écrans
        screen_files = []
        for root, _, files in os.walk(os.path.join(app_dir, "app")):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    # Vérifier si le fichier pourrait contenir un écran
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if re.search(r"class\s+\w+(?:Screen|Window|View|Page)", content) or "Screen" in content:
                            screen_files.append(file_path)
        
        logger.info(f"{len(screen_files)} fichiers potentiels d'écrans trouvés")
        
        # Analyser chaque fichier pour extraire les écrans
        for file_path in screen_files:
            rel_path = os.path.relpath(file_path, app_dir)
            logger.debug(f"Analyse du fichier: {rel_path}")
            
            # Lire le contenu du fichier
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Rechercher les classes d'écran
            screen_classes = re.finditer(
                r"class\s+(\w+)(?:Screen|Window|View|Page)?\s*\(([^)]*)\):\s*(?:\"\"\"(.*?)\"\"\")?\s*",
                content, 
                re.DOTALL
            )
            
            # Pour chaque classe trouvée
            for match in screen_classes:
                class_name = match.group(1)
                parent_class = match.group(2).strip() if match.group(2) else ""
                docstring = match.group(3).strip() if match.group(3) else ""
                
                # Si c'est potentiellement un écran
                if ("Screen" in class_name or 
                    "Window" in class_name or 
                    "View" in class_name or 
                    "Page" in class_name or
                    "Screen" in parent_class):
                    
                    # Extraction d'un titre/description depuis le docstring
                    title = ""
                    description = ""
                    
                    if docstring:
                        lines = docstring.split("\n")
                        title = lines[0].strip()
                        description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
                    
                    # Création de l'entrée d'écran
                    screen_entry = {
                        "id": f"{class_name.lower()}",
                        "name": class_name,
                        "title": title or f"Écran {class_name}",
                        "description": description or f"Écran {class_name} de l'application",
                        "file_path": rel_path,
                        "full_class_name": f"{os.path.splitext(os.path.basename(rel_path))[0]}.{class_name}",
                        "branch": self.current_branch,
                        "indexed_at": datetime.datetime.now().isoformat()
                    }
                    
                    screens.append(screen_entry)
                    logger.debug(f"Écran trouvé: {class_name}")
        
        # Sauvegarder les écrans indexés dans Firebase
        if len(screens) > 0:
            # Créer un document de métadonnées pour l'index
            metadata = {
                "id": "app_screens_index",
                "name": "Index des écrans de l'application",
                "branch": self.current_branch,
                "screen_count": len(screens),
                "created_at": datetime.datetime.now().isoformat(),
                "app_version": "1.0.1"  # À ajuster selon la version de l'app
            }
            
            # Sauvegarder les métadonnées
            self.firebase_service.set_data(collection_name, metadata)
            
            # Sauvegarder chaque écran
            for screen in screens:
                self.firebase_service.set_data(collection_name, screen)
                
            logger.info(f"Index des écrans sauvegardé dans la collection '{collection_name}'")
        
        return screens
    
    def _create_module(self, screens: list) -> bool:
        """
        Crée le module pour la branche courante dans Firebase
        Retourne True en cas de succès
        """
        if not screens:
            logger.error("Impossible de créer le module sans liste d'écrans")
            return False
        
        # Sanitize la branche pour les noms de collection
        sanitized_branch = self._sanitize_branch_name(self.current_branch)
        module_collection = f"module_indexes_modules_{sanitized_branch}"
        
        # Créer le module pour cette branche
        module_data = {
            "id": f"module_{sanitized_branch}",
            "name": f"Module {self.current_branch}",
            "description": f"Module automatiquement créé pour la branche {self.current_branch}",
            "version": "1.0.0",
            "main_screen": "dashboard",  # Écran principal du module
            "updated_at": int(time.time()),
            "branch": self.current_branch,
            "icon": "view-dashboard",  # Icône Material Design
            "type": "satellite",
            "category": "system",
            "screens_count": len(screens),
            "is_main_app": self.current_branch == "dev_application_principale_v2"  # Est-ce l'app principale?
        }
        
        # Sauvegarder le module dans la collection générique et spécifique à la branche
        self.firebase_service.set_data("module_indexes_modules", module_data)
        self.firebase_service.set_data(module_collection, module_data)
        
        # Collection pour les écrans du module
        screens_collection = f"module_indexes_screens_{module_data['id']}_{sanitized_branch}"
        
        # Créer d'abord une entrée pour l'écran principal (dashboard)
        dashboard_data = {
            "id": "dashboard",
            "name": "Tableau de bord",
            "title": "Tableau de bord",
            "description": f"Tableau de bord principal du module {self.current_branch}",
            "module_id": module_data['id'],
            "branch": self.current_branch,
            "is_main": True
        }
        
        self.firebase_service.set_data(screens_collection, dashboard_data)
        
        # Ajouter tous les écrans indexés
        for screen in screens:
            if 'id' not in screen:
                continue
                
            # Convertir au format de module
            screen_data = {
                "id": screen['id'],
                "name": screen.get('name', screen['id']),
                "title": screen.get('title', screen.get('name', screen['id'])),
                "description": screen.get('description', f"Écran {screen.get('name', screen['id'])} du module"),
                "module_id": module_data['id'],
                "branch": self.current_branch,
                "file_path": screen.get('file_path', ''),
                "full_class_name": screen.get('full_class_name', ''),
                "added_from_index": True
            }
            
            self.firebase_service.set_data(screens_collection, screen_data)
        
        logger.info(f"Module créé avec {len(screens)} écrans dans '{screens_collection}'")
        return True
    
    def is_module_initialized(self) -> bool:
        """Vérifie si le module a été correctement initialisé et indexé"""
        return self.module_indexed

# Singleton pour l'initialisation du module
_module_initializer = None

def get_module_initializer():
    """Retourne l'instance unique du ModuleInitializer"""
    global _module_initializer
    if _module_initializer is None:
        _module_initializer = ModuleInitializer()
    return _module_initializer
