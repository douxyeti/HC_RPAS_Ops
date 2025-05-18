"""
Module de logging central pour l'application HighCloud RPAS Ops.
Fournit une configuration standardisée des loggers pour l'ensemble de l'application.
"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name="hc_rpas", level=logging.INFO, log_to_file=False, log_dir="logs"):
    """
    Configure et retourne un logger avec le nom spécifié.
    
    Args:
        name (str): Nom du logger
        level (int): Niveau de log (logging.DEBUG, logging.INFO, etc.)
        log_to_file (bool): Si True, écrit également les logs dans un fichier
        log_dir (str): Répertoire où stocker les fichiers de log
        
    Returns:
        logging.Logger: Le logger configuré
    """
    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Éviter les doublons de handlers si le logger existe déjà
    if logger.handlers:
        return logger
    
    # Formatter pour la console et les fichiers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier si demandé
    if log_to_file:
        # Créer le répertoire de logs s'il n'existe pas
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True, parents=True)
        
        # Créer un fichier de log avec la date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{name}_{today}.log"
        file_handler = logging.FileHandler(
            log_path / log_file, 
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name="hc_rpas", parent=None):
    """
    Récupère un logger existant ou en crée un nouveau.
    
    Args:
        name (str): Nom du logger ou suffixe si parent est spécifié
        parent (logging.Logger): Logger parent optionnel
        
    Returns:
        logging.Logger: Le logger demandé
    """
    if parent:
        # Créer un logger enfant
        return logging.getLogger(f"{parent.name}.{name}")
    
    # Récupérer un logger existant
    return logging.getLogger(name)
