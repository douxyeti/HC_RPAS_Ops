"""
Architecture modulaire HC_RPAS_Ops
Ce dossier contient les nouveaux modules développés selon l'architecture modulaire
"""

import os
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger("hc_rpas.modules")

def discover_modules() -> List[Dict[str, Any]]:
    """
    Découvre tous les modules disponibles dans ce dossier
    """
    modules = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Parcourir les sous-dossiers (potentiels modules)
        for item in os.listdir(current_dir):
            module_dir = os.path.join(current_dir, item)
            
            # Vérifier si c'est un dossier et s'il contient module_info.json
            if os.path.isdir(module_dir) and os.path.exists(os.path.join(module_dir, 'module_info.json')):
                try:
                    # Charger les infos du module
                    with open(os.path.join(module_dir, 'module_info.json'), 'r', encoding='utf-8') as f:
                        module_info = json.load(f)
                    
                    # Ajouter les métadonnées du chemin
                    module_info['path'] = module_dir
                    modules.append(module_info)
                    
                    logger.info(f"Module trouvé: {module_info.get('name', item)}")
                except Exception as e:
                    logger.warning(f"Erreur lors du chargement du module {item}: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur lors de la découverte des modules: {str(e)}")
    
    return modules
