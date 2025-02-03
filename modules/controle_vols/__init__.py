pip uninstall kivy -y
pip install kivy[base] kivy_examples --pre --extra-index-url https://kivy.org/downloads/simple/
pip uninstall kivy -y
pip install kivy[base] kivy_examples --pre --extra-index-url https://kivy.org/downloads/simple/
"""
Module de contrôle des vols pour HighCloud RPAS Operations Manager.
Gère les opérations liées aux vols de drones, incluant la planification,
l'exécution et le suivi des missions.
"""

from .models import *
from .viewmodels import *
from .services import *
