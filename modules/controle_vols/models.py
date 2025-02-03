"""
Modèles de données pour le module de contrôle des vols.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class Vol(Base):
    __tablename__ = 'vols'
    
    id = Column(Integer, primary_key=True)
    numero_vol = Column(String(50), unique=True, nullable=False)
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime)
    statut = Column(String(20), nullable=False)  # planifié, en_cours, terminé, annulé
    pilote_id = Column(Integer, ForeignKey('personnel.id'), nullable=False)
    drone_id = Column(Integer, ForeignKey('drones.id'), nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=False)
    
    # Relations
    pilote = relationship("Personnel")
    drone = relationship("Drone")
    mission = relationship("Mission")
    checkpoints = relationship("Checkpoint", back_populates="vol")
    
    def __repr__(self):
        return f"<Vol {self.numero_vol}>"

class Checkpoint(Base):
    __tablename__ = 'checkpoints'
    
    id = Column(Integer, primary_key=True)
    vol_id = Column(Integer, ForeignKey('vols.id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    ordre = Column(Integer, nullable=False)
    atteint = Column(Boolean, default=False)
    
    # Relations
    vol = relationship("Vol", back_populates="checkpoints")
    
    def __repr__(self):
        return f"<Checkpoint {self.ordre} du vol {self.vol_id}>"
