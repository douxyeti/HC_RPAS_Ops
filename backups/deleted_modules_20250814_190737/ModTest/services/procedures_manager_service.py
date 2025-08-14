from app.services.firebase_service import FirebaseService
import unicodedata
import re
from datetime import datetime

class ProceduresManagerService:
    """Service pour la gestion des procédures et leurs étapes"""
    
    def __init__(self):
        self.db = FirebaseService()
        self.collection = 'procedures'
        
    def get_all_procedures(self):
        """Récupère toutes les procédures"""
        print("[DEBUG] ProceduresManagerService.get_all_procedures - Début de la récupération")
        procedures = self.db.get_collection(self.collection)
        print(f"[DEBUG] ProceduresManagerService.get_all_procedures - {len(procedures)} procédures récupérées")
        return procedures
        
    def get_procedure(self, procedure_id):
        """Récupère une procédure par son ID"""
        try:
            procedure = self.db.get_document(self.collection, procedure_id)
            return procedure if procedure else None
        except Exception as e:
            print(f"Erreur lors de la récupération de la procédure : {e}")
            return None
        
    def create_procedure(self, procedure_data):
        """Crée une nouvelle procédure
        
        Args:
            procedure_data: Dictionnaire contenant les données de la procédure :
                      - name: Nom de la procédure
                      - description: Description de la procédure
        """
        procedure_id = self.normalize_string(procedure_data['name'])
        now = datetime.now().isoformat()
        
        new_procedure = {
            'id': procedure_id,
            'name': procedure_data['name'],
            'description': procedure_data.get('description', ''),
            'created_at': now,
            'updated_at': now,
            'steps': [],
            'status': 'active'
        }
        
        self.db.add_document_with_id(self.collection, procedure_id, new_procedure)
        return new_procedure
        
    def update_procedure(self, procedure_id, procedure_data):
        """Met à jour une procédure existante"""
        if not procedure_id or not procedure_data:
            return False
            
        try:
            # Mettre à jour dans Firebase
            self.db.update_document('procedures', procedure_id, procedure_data)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la procédure : {e}")
            return False
        
    def delete_procedure(self, procedure_id):
        """Supprime une procédure"""
        self.db.delete_document(self.collection, procedure_id)
        
    def add_step(self, procedure_id, step_data):
        """Ajoute une étape à une procédure"""
        procedure = self.get_procedure(procedure_id)
        if not procedure:
            return None
            
        steps = procedure.get('steps', [])
        target_order = step_data.get('order', len(steps) + 1)
        
        # Décaler les étapes existantes
        for step in steps:
            if step['order'] >= target_order:
                step['order'] += 1
        
        new_step = {
            'id': f"step_{len(steps) + 1}",
            'name': step_data['name'],
            'description': step_data.get('description', ''),
            'order': target_order,
            'duration': step_data.get('duration', 0),
            'status': 'active'
        }
        
        steps.append(new_step)
        procedure['steps'] = sorted(steps, key=lambda x: x['order'])
        procedure['updated_at'] = datetime.now().isoformat()
        
        self.db.add_document_with_id(self.collection, procedure_id, procedure)
        return new_step
        
    def update_step(self, procedure_id, step_id, step_data):
        """Met à jour une étape d'une procédure"""
        procedure = self.get_procedure(procedure_id)
        if not procedure:
            return None
            
        steps = procedure.get('steps', [])
        for i, step in enumerate(steps):
            if step['id'] == step_id:
                steps[i].update({
                    'name': step_data.get('name', step['name']),
                    'description': step_data.get('description', step['description']),
                    'duration': step_data.get('duration', step['duration']),
                    'status': step_data.get('status', step['status'])
                })
                procedure['updated_at'] = datetime.now().isoformat()
                self.db.add_document_with_id(self.collection, procedure_id, procedure)
                return steps[i]
        return None
        
    def delete_step(self, procedure_id, step_id):
        """Supprime une étape d'une procédure"""
        procedure = self.get_procedure(procedure_id)
        if not procedure:
            return False
            
        steps = procedure.get('steps', [])
        procedure['steps'] = [s for s in steps if s['id'] != step_id]
        procedure['updated_at'] = datetime.now().isoformat()
        
        # Réorganiser les ordres des étapes restantes
        for i, step in enumerate(procedure['steps'], 1):
            step['order'] = i
            
        self.db.add_document_with_id(self.collection, procedure_id, procedure)
        return True
        
    def reorder_steps(self, procedure_id, step_orders):
        """Met à jour l'ordre des étapes
        
        Args:
            step_orders: Liste de tuples (step_id, new_order)
        """
        procedure = self.get_procedure(procedure_id)
        if not procedure:
            return False
            
        steps_dict = {step['id']: step for step in procedure['steps']}
        for step_id, new_order in step_orders:
            if step_id in steps_dict:
                steps_dict[step_id]['order'] = new_order
                
        procedure['steps'] = sorted(steps_dict.values(), key=lambda x: x['order'])
        procedure['updated_at'] = datetime.now().isoformat()
        
        self.db.add_document_with_id(self.collection, procedure_id, procedure)
        return True
        
    @staticmethod
    def normalize_string(s):
        """Normalise une chaîne pour l'utiliser comme ID"""
        # Convertir en minuscules et remplacer les accents
        s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
        # Remplacer les espaces par des underscores
        s = re.sub(r'[^a-z0-9]+', '_', s.lower())
        # Supprimer les underscores en début et fin
        return s.strip('_')
