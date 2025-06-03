"""
Outil d'analyse du code existant pour l'architecture modulaire HC_RPAS_Ops
Cet outil analyse la structure actuelle de l'application sans modifier le code
"""

import os
import re
import json
from typing import Dict, List, Any
import logging

# Configuration du logger
logger = logging.getLogger("hc_rpas.analyzer")

def analyze_existing_modules(app_path: str) -> Dict[str, Any]:
    """
    Analyse la structure actuelle pour identifier les modules potentiels
    sans modifier quoi que ce soit
    """
    results = {
        "potential_modules": [],
        "import_dependencies": {},
        "screen_registry": [],
        "mqtt_topics": []
    }
    
    logger.info(f"Analyse du code dans {app_path}")
    
    # Parcourir les fichiers Python pour identifier les imports et les classes d'écran
    for root, _, files in os.walk(app_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, app_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Chercher les écrans
                        if '_screen.py' in file.lower():
                            # Rechercher les classes d'écran
                            screen_classes = re.findall(r'class\s+(\w+Screen)\(', content)
                            
                            for screen_class in screen_classes:
                                results["screen_registry"].append({
                                    "file": rel_path,
                                    "class": screen_class,
                                    "potential_module": _infer_module_from_path(rel_path)
                                })
                        
                        # Chercher les imports pour analyser les dépendances
                        imports = re.findall(r'(?:from|import)\s+([\w\.]+)', content)
                        if imports:
                            results["import_dependencies"][rel_path] = imports
                        
                        # Rechercher les topics MQTT (selon la structure standardisée)
                        mqtt_topics = re.findall(r'[\'\"](hc_rpas/modules/[\w/]+)[\'\"]', content)
                        if mqtt_topics:
                            for topic in mqtt_topics:
                                if topic not in results["mqtt_topics"]:
                                    results["mqtt_topics"].append(topic)
                except Exception as e:
                    logger.error(f"Erreur lors de l'analyse de {file_path}: {str(e)}")
    
    # Inférer les modules potentiels
    module_candidates = set()
    for screen in results["screen_registry"]:
        if screen["potential_module"]:
            module_candidates.add(screen["potential_module"])
    
    # Analyser les topics MQTT pour trouver des indices de modules
    for topic in results["mqtt_topics"]:
        parts = topic.split('/')
        if len(parts) > 2 and parts[0] == "hc_rpas" and parts[1] == "modules":
            module_candidates.add(parts[2])
    
    # Créer des entrées pour les modules potentiels
    for module_name in sorted(module_candidates):
        # Compter les écrans pour ce module
        screens = [s for s in results["screen_registry"] 
                   if s["potential_module"] == module_name]
        
        # Trouver les topics MQTT associés à ce module
        module_topics = [t for t in results["mqtt_topics"] 
                         if f"hc_rpas/modules/{module_name}/" in t]
        
        results["potential_modules"].append({
            "name": module_name,
            "screens_count": len(screens),
            "screens": screens,
            "mqtt_topics": module_topics
        })
    
    return results

def _infer_module_from_path(rel_path: str) -> str:
    """Infère le nom du module à partir du chemin du fichier"""
    parts = rel_path.split(os.sep)
    
    # Essayer de trouver un nom de module potentiel
    module_indicators = ["views", "screens", "services"]
    
    for i, part in enumerate(parts):
        if part.lower() in module_indicators and i+1 < len(parts):
            # Nettoyage du nom de module
            module_name = parts[i+1].replace("_screen", "").replace(".py", "")
            return module_name
    
    # Cas spécial : chemin contient "modules"
    for i, part in enumerate(parts):
        if part.lower() == "modules" and i+1 < len(parts):
            return parts[i+1]
    
    return ""

def generate_report(results: Dict[str, Any], output_file: str = "module_analysis.json"):
    """Génère un rapport d'analyse sans modifier le code"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Rapport d'analyse généré: {output_file}")
    print(f"Modules potentiels identifiés: {len(results['potential_modules'])}")
    
    for module in results["potential_modules"]:
        print(f"- {module['name']}: {module['screens_count']} écrans, {len(module['mqtt_topics'])} topics MQTT")
        
        # Afficher les écrans trouvés
        if module['screens']:
            print("  Écrans:")
            for screen in module['screens']:
                print(f"    * {screen['class']} ({screen['file']})")
        
        # Afficher les topics MQTT
        if module['mqtt_topics']:
            print("  Topics MQTT:")
            for topic in module['mqtt_topics']:
                print(f"    * {topic}")
        
        print("")

if __name__ == "__main__":
    import sys
    import argparse
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Analyse la structure du code HC_RPAS_Ops")
    parser.add_argument("--path", default="app", help="Chemin de l'application à analyser")
    parser.add_argument("--output", default="module_analysis.json", help="Fichier de sortie pour le rapport")
    args = parser.parse_args()
    
    print(f"Analyse du code dans {args.path}...")
    results = analyze_existing_modules(args.path)
    generate_report(results, args.output)
    print(f"Analyse terminée, rapport généré dans {args.output}")
