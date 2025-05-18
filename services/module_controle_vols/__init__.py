"""
Module de contrôle opérationnel des vols pour HighCloud RPAS Ops.
Ce module peut être utilisé de manière autonome ou intégré à l'application principale.
"""

from .module_registry import ModuleRegistry

def initialize(firebase_service):
    """
    Initialise le module de contrôle des vols
    
    Args:
        firebase_service: Service Firebase de l'application principale
        
    Returns:
        True si l'initialisation a réussi, False sinon
    """
    registry = ModuleRegistry.get_instance()
    return registry.initialize(firebase_service)

def get_registry():
    """
    Retourne le registre du module pour accéder aux écrans
    
    Returns:
        Instance du ModuleRegistry
    """
    return ModuleRegistry.get_instance()
