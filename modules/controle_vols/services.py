"""
Services pour le module de contrôle des vols.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Vol, Checkpoint
from app.services.base import BaseService

class ControlVolService(BaseService):
    def __init__(self, session: Session):
        super().__init__(session)
        
    def creer_vol(self, numero_vol: str, date_debut: datetime, 
                  pilote_id: int, drone_id: int, mission_id: int) -> Vol:
        """Crée un nouveau vol dans le système."""
        vol = Vol(
            numero_vol=numero_vol,
            date_debut=date_debut,
            statut='planifié',
            pilote_id=pilote_id,
            drone_id=drone_id,
            mission_id=mission_id
        )
        self.session.add(vol)
        self.session.commit()
        return vol
        
    def demarrer_vol(self, vol_id: int) -> Vol:
        """Démarre un vol planifié."""
        vol = self.session.query(Vol).get(vol_id)
        if vol and vol.statut == 'planifié':
            vol.statut = 'en_cours'
            vol.date_debut = datetime.now()
            self.session.commit()
        return vol
        
    def terminer_vol(self, vol_id: int) -> Vol:
        """Termine un vol en cours."""
        vol = self.session.query(Vol).get(vol_id)
        if vol and vol.statut == 'en_cours':
            vol.statut = 'terminé'
            vol.date_fin = datetime.now()
            self.session.commit()
        return vol
        
    def ajouter_checkpoint(self, vol_id: int, latitude: float, 
                          longitude: float, altitude: float, ordre: int) -> Checkpoint:
        """Ajoute un checkpoint à un vol."""
        checkpoint = Checkpoint(
            vol_id=vol_id,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            ordre=ordre
        )
        self.session.add(checkpoint)
        self.session.commit()
        return checkpoint
        
    def marquer_checkpoint_atteint(self, checkpoint_id: int) -> Checkpoint:
        """Marque un checkpoint comme atteint."""
        checkpoint = self.session.query(Checkpoint).get(checkpoint_id)
        if checkpoint:
            checkpoint.atteint = True
            self.session.commit()
        return checkpoint
