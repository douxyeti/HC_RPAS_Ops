"""
Script de test pour vérifier l'intégration du module contrôle de vols
"""
import os
import sys
import logging
import importlib

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hc_rpas.test_integration")

def test_module_discovery():
    """Teste la découverte du module contrôle de vols"""
    try:
        # Importer le module de découverte
        from app.utils.module_discovery import ModuleDiscovery
        
        # Créer un service Firebase minimal pour les tests
        class MockFirebaseService:
            def get_collection(self, collection_name):
                return []  # Simuler une collection vide pour forcer la découverte par système de fichiers
        
        # Créer une instance de ModuleDiscovery
        discovery = ModuleDiscovery(MockFirebaseService())
        
        # Récupérer les modules installés
        modules = discovery.get_installed_modules()
        
        # Vérifier si le module contrôle de vols est détecté
        controle_vols_found = False
        for module in modules:
            logger.info(f"Module détecté: {module.get('id')} - {module.get('name')}")
            if module.get('id') == 'controle_vols':
                controle_vols_found = True
                logger.info(f"Module contrôle de vols trouvé: {module}")
        
        if controle_vols_found:
            logger.info("✅ Module contrôle de vols correctement détecté")
        else:
            logger.warning("❌ Module contrôle de vols non détecté")
            
        return controle_vols_found
    except Exception as e:
        logger.error(f"Erreur lors du test de découverte: {str(e)}")
        return False

def test_module_manager():
    """Teste le gestionnaire de modules avec le module contrôle de vols"""
    try:
        # Importer le gestionnaire de modules
        from app.utils.module_manager import ModuleManager
        
        # Créer une instance du gestionnaire
        manager = ModuleManager()
        
        # Découvrir les modules
        modules_info = manager.discover_modules()
        
        # Vérifier si le module contrôle de vols est découvert
        controle_vols_found = False
        for module in modules_info:
            logger.info(f"Module découvert: {module.get('id')} - {module.get('name')}")
            if module.get('id') == 'controle_vols':
                controle_vols_found = True
                logger.info(f"Module contrôle de vols découvert: {module}")
        
        if controle_vols_found:
            logger.info("✅ Module contrôle de vols correctement découvert par le gestionnaire")
        else:
            logger.warning("❌ Module contrôle de vols non découvert par le gestionnaire")
        
        # Tentative de chargement du module
        if controle_vols_found:
            result = manager.load_module('controle_vols')
            if result:
                logger.info("✅ Module contrôle de vols chargé avec succès")
                
                # Vérifier les écrans disponibles
                module_instance = manager.modules.get('controle_vols')
                if module_instance and hasattr(module_instance, 'get_screens'):
                    screens = module_instance.get_screens()
                    logger.info(f"Écrans disponibles: {len(screens)}")
                    for screen in screens:
                        logger.info(f"Écran: {screen.get('id')} - {screen.get('name')}")
            else:
                logger.warning("❌ Échec du chargement du module contrôle de vols")
        
        return controle_vols_found
    except Exception as e:
        logger.error(f"Erreur lors du test du gestionnaire de modules: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Début des tests d'intégration ===")
    
    # Tester la découverte du module
    discovery_result = test_module_discovery()
    
    # Tester le gestionnaire de modules
    manager_result = test_module_manager()
    
    # Afficher le résultat global
    if discovery_result and manager_result:
        logger.info("✅ Tests d'intégration réussis")
    else:
        logger.warning("❌ Tests d'intégration échoués")
    
    logger.info("=== Fin des tests d'intégration ===")
