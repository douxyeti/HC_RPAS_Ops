"""
ViewModels pour le module de contrôle des vols.
"""
from datetime import datetime
from typing import List, Optional
from kivymd.uix.snackbar import Snackbar
from app.viewmodels.base import BaseViewModel
from .services import ControlVolService
from .models import Vol, Checkpoint

class ControlVolViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()
        self.service = ControlVolService(self.session)
        self.vol_actif = None
        
    def planifier_vol(self, numero_vol: str, date_debut: datetime, 
                     pilote_id: int, drone_id: int, mission_id: int) -> bool:
        """Planifie un nouveau vol."""
        try:
            vol = self.service.creer_vol(
                numero_vol=numero_vol,
                date_debut=date_debut,
                pilote_id=pilote_id,
                drone_id=drone_id,
                mission_id=mission_id
            )
            self.notifier_succes("Vol planifié avec succès")
            return True
        except Exception as e:
            self.notifier_erreur(f"Erreur lors de la planification du vol: {str(e)}")
            return False
            
    def demarrer_vol(self, vol_id: int) -> bool:
        """Démarre un vol planifié."""
        try:
            vol = self.service.demarrer_vol(vol_id)
            if vol and vol.statut == 'en_cours':
                self.vol_actif = vol
                self.notifier_succes("Vol démarré avec succès")
                return True
            else:
                self.notifier_erreur("Impossible de démarrer le vol")
                return False
        except Exception as e:
            self.notifier_erreur(f"Erreur lors du démarrage du vol: {str(e)}")
            return False
            
    def terminer_vol(self) -> bool:
        """Termine le vol actif."""
        if not self.vol_actif:
            self.notifier_erreur("Aucun vol actif")
            return False
            
        try:
            vol = self.service.terminer_vol(self.vol_actif.id)
            if vol and vol.statut == 'terminé':
                self.vol_actif = None
                self.notifier_succes("Vol terminé avec succès")
                return True
            else:
                self.notifier_erreur("Impossible de terminer le vol")
                return False
        except Exception as e:
            self.notifier_erreur(f"Erreur lors de la terminaison du vol: {str(e)}")
            return False
            
    def notifier_succes(self, message: str):
        """Affiche une notification de succès."""
        Snackbar(text=message, bg_color=(0, 0.7, 0, 1)).open()
        
    def notifier_erreur(self, message: str):
        """Affiche une notification d'erreur."""
        Snackbar(text=message, bg_color=(0.8, 0, 0, 1)).open()
