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
        Vérifie si une indexation est nécessaire
        Retourne True si l'index n'existe pas dans Firebase
        """
        if not self.firebase_service:
            logger.error("Firebase n'est pas initialisé. Impossible de vérifier l'index.")
            return False
        
        # Nom de collection spécifique à la branche pour l'index des écrans
        sanitized_branch = self._sanitize_branch_name(self.current_branch)
        collection_name = f"app_screens_index_{sanitized_branch}"
        
        # Vérifie si la collection existe et contient des données
        try:
            documents = self.firebase_service.get_collection(collection_name)
            if documents and len(documents) > 0:
                logger.info(f"Collection d'index trouvée avec {len(documents)} documents")
                return False
            else:
                logger.info(f"Collection d'index vide ou inexistante: {collection_name}")
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'index: {e}")
            return True
    
    def _run_indexing(self) -> bool:
        """
        Exécute le script d'indexation pour la branche courante
        Retourne True en cas de succès
        """
        try:
            # Construction du chemin vers les scripts
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            scripts_dir = os.path.join(base_dir, "scripts")
            
            # Exécuter le script d'indexation
            index_script = os.path.join(scripts_dir, "index_app_screens.py")
            if not os.path.exists(index_script):
                logger.error(f"Le script d'indexation n'existe pas: {index_script}")
                return False
            
            logger.info(f"Exécution du script d'indexation: {index_script}")
            result = subprocess.run(
                [sys.executable, index_script],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Erreur lors de l'indexation: {result.stderr}")
                return False
            
            logger.info(f"Indexation réussie: {result.stdout}")
            
            # Exécuter le script de création du module
            module_script = os.path.join(scripts_dir, "create_app_index_module.py")
            if not os.path.exists(module_script):
                logger.error(f"Le script de création du module n'existe pas: {module_script}")
                return False
            
            logger.info(f"Exécution du script de création du module: {module_script}")
            result = subprocess.run(
                [sys.executable, module_script],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Erreur lors de la création du module: {result.stderr}")
                return False
            
            logger.info(f"Création du module réussie: {result.stdout}")
            self.module_indexed = True
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des scripts d'indexation: {e}")
            return False
    
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
