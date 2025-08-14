"""
Outil de clonage de module pour l'architecture modulaire HC_RPAS_Ops
Permet de dupliquer et personnaliser un module existant pour en créer un nouveau
"""

import os
import sys
import shutil
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuration du logger
logger = logging.getLogger("hc_rpas.clone_module")

class ModuleCloner:
    """Utilitaire pour cloner un module existant et créer un nouveau module"""
    
    def __init__(self, source_module_path: str, target_module_id: str, target_dir: Optional[str] = None):
        """
        Initialise le clonage d'un module
        
        Args:
            source_module_path: Chemin absolu vers le module source à cloner
            target_module_id: Identifiant du nouveau module à créer
            target_dir: Répertoire cible pour le nouveau module (optionnel)
        """
        self.source_path = os.path.abspath(source_module_path)
        self.target_module_id = target_module_id
        
        # Déterminer le répertoire parent si non spécifié
        if target_dir:
            self.target_dir = os.path.abspath(target_dir)
        else:
            # Par défaut, créer le module dans le même répertoire parent
            parent_dir = os.path.dirname(self.source_path)
            self.target_dir = parent_dir
        
        # Créer le chemin complet du nouveau module
        self.target_path = os.path.join(self.target_dir, self.target_module_id)
        
        # Extraire les informations du module source
        self.source_module_info = self._load_source_module_info()
    
    def _load_source_module_info(self) -> Dict[str, Any]:
        """Charge les informations du module source"""
        info_path = os.path.join(self.source_path, 'module_info.json')
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement des infos du module source: {str(e)}")
        else:
            logger.warning(f"Fichier module_info.json introuvable dans {self.source_path}")
        
        # Retourner un dict vide si le fichier n'existe pas
        return {}
    
    def validate(self) -> bool:
        """Valide les paramètres avant le clonage"""
        # Vérifier que le chemin source existe
        if not os.path.exists(self.source_path):
            logger.error(f"Module source introuvable: {self.source_path}")
            return False
        
        # Vérifier que c'est un dossier
        if not os.path.isdir(self.source_path):
            logger.error(f"Le chemin source n'est pas un dossier: {self.source_path}")
            return False
        
        # Vérifier que le module cible n'existe pas déjà
        if os.path.exists(self.target_path):
            logger.error(f"Le module cible existe déjà: {self.target_path}")
            return False
        
        # Vérifier que le répertoire parent existe
        parent_dir = os.path.dirname(self.target_path)
        if not os.path.exists(parent_dir):
            logger.error(f"Le répertoire parent du module cible n'existe pas: {parent_dir}")
            return False
        
        # Vérifier l'identifiant du module
        if not re.match(r'^[a-z0-9_]+$', self.target_module_id):
            logger.error(f"Identifiant de module invalide (doit être en minuscules, chiffres et underscores): {self.target_module_id}")
            return False
        
        return True
    
    def clone(self, new_module_name: str = "", author: str = "") -> bool:
        """Clone le module source vers le nouveau module"""
        if not self.validate():
            return False
        
        try:
            # Créer le répertoire cible
            os.makedirs(self.target_path, exist_ok=True)
            logger.info(f"Répertoire créé: {self.target_path}")
            
            # Copier les fichiers et dossiers du module source
            self._copy_module_files()
            
            # Mettre à jour les références dans les fichiers
            self._update_module_references(new_module_name, author)
            
            logger.info(f"Module cloné avec succès: {self.target_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du clonage du module: {str(e)}")
            # En cas d'erreur, essayer de nettoyer
            if os.path.exists(self.target_path):
                try:
                    shutil.rmtree(self.target_path)
                    logger.info(f"Nettoyage du répertoire cible après erreur: {self.target_path}")
                except:
                    pass
            return False
    
    def _copy_module_files(self):
        """Copie les fichiers du module source vers le module cible"""
        for root, dirs, files in os.walk(self.source_path):
            # Calculer le chemin relatif
            rel_path = os.path.relpath(root, self.source_path)
            target_dir = os.path.join(self.target_path, rel_path) if rel_path != '.' else self.target_path
            
            # Créer le répertoire cible s'il n'existe pas
            os.makedirs(target_dir, exist_ok=True)
            
            # Copier les fichiers normaux
            for file in files:
                # Ignorer les fichiers temporaires et __pycache__
                if file.endswith('.pyc') or file.startswith('__pycache__') or file.startswith('.'):
                    continue
                
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                
                shutil.copy2(source_file, target_file)
                logger.debug(f"Fichier copié: {os.path.relpath(target_file, self.target_path)}")
        
        logger.info(f"Tous les fichiers ont été copiés vers {self.target_path}")
    
    def _update_module_references(self, new_module_name: str, author: str):
        """Met à jour les références dans les fichiers du nouveau module"""
        source_id = self.source_module_info.get('id', os.path.basename(self.source_path))
        source_name = self.source_module_info.get('name', source_id.replace('_', ' ').title())
        
        # Déterminer le nouveau nom du module si non spécifié
        if not new_module_name:
            new_module_name = self.target_module_id.replace('_', ' ').title()
        
        # Parcourir tous les fichiers du nouveau module
        for root, _, files in os.walk(self.target_path):
            for file in files:
                # Ignorer les fichiers binaires et temporaires
                if file.endswith(('.pyc', '.pyo', '.so', '.pyd', '.db', '.sqlite', '.png', '.jpg', '.jpeg', '.gif')):
                    continue
                
                file_path = os.path.join(root, file)
                
                # Traitement spécial pour module_info.json
                if file == 'module_info.json':
                    self._update_module_info(file_path, new_module_name, author)
                    continue
                
                # Mettre à jour les références dans les fichiers Python et autres textes
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Remplacer les occurrences
                    updated_content = content
                    # Remplacer l'ID du module (cas sensible)
                    updated_content = re.sub(r'\b' + re.escape(source_id) + r'\b', self.target_module_id, updated_content)
                    # Remplacer le nom du module (cas sensible)
                    updated_content = re.sub(re.escape(source_name), new_module_name, updated_content)
                    # Remplacer dans les imports
                    updated_content = re.sub(r'from\s+' + re.escape(source_id), f'from {self.target_module_id}', updated_content)
                    updated_content = re.sub(r'import\s+' + re.escape(source_id), f'import {self.target_module_id}', updated_content)
                    # Remplacer dans les logs
                    updated_content = re.sub(r'\"hc_rpas\.' + re.escape(source_id), f'"hc_rpas.{self.target_module_id}', updated_content)
                    # Remplacer dans les topics MQTT
                    updated_content = re.sub(r'hc_rpas/modules/' + re.escape(source_id), f'hc_rpas/modules/{self.target_module_id}', updated_content)
                    
                    # Écrire le contenu mis à jour
                    if content != updated_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        logger.debug(f"Références mises à jour dans: {os.path.relpath(file_path, self.target_path)}")
                
                except Exception as e:
                    logger.warning(f"Impossible de mettre à jour les références dans {file_path}: {str(e)}")
        
        logger.info(f"Toutes les références ont été mises à jour dans le module {self.target_module_id}")
    
    def _update_module_info(self, info_path: str, new_module_name: str, author: str):
        """Met à jour le fichier module_info.json avec les nouvelles informations"""
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                module_info = json.load(f)
            
            # Mettre à jour les informations
            module_info['id'] = self.target_module_id
            module_info['name'] = new_module_name
            
            # Mettre à jour l'auteur si spécifié
            if author:
                module_info['author'] = author
            
            # Mettre à jour les topics MQTT si définis
            if 'mqtt_topics' in module_info:
                for i, topic in enumerate(module_info['mqtt_topics']):
                    module_info['mqtt_topics'][i] = topic.replace(
                        f"hc_rpas/modules/{self.source_module_info.get('id', '')}",
                        f"hc_rpas/modules/{self.target_module_id}"
                    )
            
            # Enregistrer les modifications
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(module_info, f, indent=2)
            
            logger.info(f"Informations du module mises à jour dans: {os.path.relpath(info_path, self.target_path)}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des informations du module: {str(e)}")

def clone_module_main():
    """Point d'entrée principal pour l'outil en ligne de commande"""
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Parser les arguments
    import argparse
    parser = argparse.ArgumentParser(description="Cloner un module existant pour en créer un nouveau")
    parser.add_argument("source", help="Chemin vers le module source")
    parser.add_argument("target_id", help="ID du nouveau module (minuscules, chiffres et underscores)")
    parser.add_argument("--target-dir", help="Répertoire où créer le nouveau module")
    parser.add_argument("--name", help="Nom du nouveau module")
    parser.add_argument("--author", help="Auteur du nouveau module")
    args = parser.parse_args()
    
    # Créer et exécuter le cloneur
    cloner = ModuleCloner(args.source, args.target_id, args.target_dir)
    if cloner.clone(args.name, args.author):
        print(f"✅ Module cloné avec succès dans: {cloner.target_path}")
        return 0
    else:
        print(f"❌ Échec du clonage du module. Consultez les logs pour plus de détails.")
        return 1

if __name__ == "__main__":
    sys.exit(clone_module_main())
