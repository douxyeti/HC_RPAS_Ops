#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour indexer toutes les fenêtres de l'application principale
et sauvegarder cet index dans Firebase sous une collection dédiée
avec identification claire à la branche actuelle.
"""

import os
import re
import sys
import subprocess
import json
import datetime
from typing import Dict, List, Any, Optional

# Ajouter le répertoire parent au path pour pouvoir importer les modules de l'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services nécessaires de l'application
from app.services.firebase_service import FirebaseService

# Nom de la collection pour l'index des fenêtres
BRANCH_NAME = "dev_application_principale_v2"
COLLECTION_NAME = f"app_screens_index_{BRANCH_NAME}"

class ScreenIndexer:
    """Classe pour indexer les fenêtres de l'application principale"""
    
    def __init__(self):
        self.firebase_service = FirebaseService()
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.screens = []
        
    def get_current_branch(self) -> str:
        """Obtenir le nom de la branche Git actuelle"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.app_dir,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Erreur lors de la récupération de la branche Git: {e}")
            return BRANCH_NAME  # Fallback à la valeur connue
    
    def find_screen_files(self) -> List[str]:
        """Trouver tous les fichiers Python qui pourraient contenir des écrans"""
        screen_files = []
        for root, _, files in os.walk(os.path.join(self.app_dir, "app")):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    # Lire le contenu du fichier pour vérifier s'il contient potentiellement un écran
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        # Recherche les classes qui pourraient être des écrans
                        if re.search(r"class\s+\w+(?:Screen|Window|View|Page)", content) or "Screen" in content:
                            screen_files.append(file_path)
        return screen_files
    
    def extract_screen_info(self, file_path: str) -> List[Dict[str, Any]]:
        """Extraire les informations sur les écrans d'un fichier"""
        screens = []
        rel_path = os.path.relpath(file_path, self.app_dir)
        
        # Lire le contenu du fichier
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Rechercher les classes d'écran
        screen_classes = re.finditer(
            r"class\s+(\w+)(?:Screen|Window|View|Page)?\s*\(([^)]*)\):\s*(?:\"\"\"(.*?)\"\"\")?",
            content, 
            re.DOTALL
        )
        
        # Pour chaque classe trouvée
        for match in screen_classes:
            class_name = match.group(1)
            parent_class = match.group(2).strip() if match.group(2) else ""
            docstring = match.group(3).strip() if match.group(3) else ""
            
            # Si le nom de la classe contient "Screen" ou la classe hérite de quelque chose avec "Screen"
            if ("Screen" in class_name or 
                "Window" in class_name or 
                "View" in class_name or 
                "Page" in class_name or
                "Screen" in parent_class):
                
                # Extraction d'un titre/description court depuis le docstring
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
                    "description": description or f"Écran {class_name} de l'application principale",
                    "file_path": rel_path,
                    "full_class_name": f"{os.path.splitext(os.path.basename(rel_path))[0]}.{class_name}",
                    "branch": BRANCH_NAME,
                    "indexed_at": datetime.datetime.now().isoformat()
                }
                
                screens.append(screen_entry)
                
        return screens
    
    def index_all_screens(self):
        """Indexer toutes les fenêtres de l'application"""
        screen_files = self.find_screen_files()
        
        for file_path in screen_files:
            print(f"Analyse du fichier: {file_path}")
            screen_infos = self.extract_screen_info(file_path)
            self.screens.extend(screen_infos)
        
        print(f"Nombre total d'écrans indexés: {len(self.screens)}")
        
    def save_to_firebase(self):
        """Sauvegarder l'index dans Firebase"""
        # Créer un document principal pour l'index
        metadata = {
            "id": "app_screens_index",
            "name": "Index des écrans de l'application principale",
            "branch": BRANCH_NAME,
            "screen_count": len(self.screens),
            "created_at": datetime.datetime.now().isoformat(),
            "app_version": "1.0.1"  # À ajuster selon la version de l'app
        }
        
        # Ajouter le document de métadonnées
        self.firebase_service.set_data(COLLECTION_NAME, metadata)
        
        # Ajouter chaque écran comme document distinct
        for screen in self.screens:
            screen_id = screen.get('id', f"screen_{len(self.screens)}")
            # S'assurer que chaque document a un ID unique
            self.firebase_service.set_data(COLLECTION_NAME, screen)
            
        print(f"Index des écrans sauvegardé dans la collection Firebase '{COLLECTION_NAME}'")

def main():
    """Fonction principale"""
    indexer = ScreenIndexer()
    current_branch = indexer.get_current_branch()
    
    print(f"Indexation des écrans de l'application principale sur la branche: {current_branch}")
    
    # Vérifier que nous sommes sur la bonne branche
    if current_branch != BRANCH_NAME:
        print(f"ATTENTION: La branche actuelle ({current_branch}) ne correspond pas à la branche cible ({BRANCH_NAME}).")
        response = input("Voulez-vous continuer quand même? (o/n): ")
        if response.lower() != "o":
            print("Opération annulée.")
            return
    
    indexer.index_all_screens()
    indexer.save_to_firebase()
    print("Indexation terminée avec succès!")

if __name__ == "__main__":
    main()
