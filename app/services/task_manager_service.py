from app.services.firebase_service import FirebaseService

class TaskManagerService:
    """Service pour la gestion des tâches"""
    
    def __init__(self):
        print("[DEBUG] TaskManagerService.__init__ - Initialisation du service")
        self.db = FirebaseService()
        self.collection = 'roles'
        
    def get_role_by_name(self, role_name):
        """Récupère un rôle par son nom"""
        print(f"[DEBUG] TaskManagerService.get_role_by_name - Recherche du rôle '{role_name}'")
        try:
            roles = self.db.get_collection(self.collection)
            role = next((r for r in roles if r.get('name') == role_name), None)
            return role
        except Exception as e:
            print(f"[ERROR] TaskManagerService.get_role_by_name - Erreur: {str(e)}")
            return None
        
    def get_all_tasks(self, role_id):
        """Récupère toutes les tâches d'un rôle"""
        print(f"[DEBUG] TaskManagerService.get_all_tasks - Récupération des tâches pour le rôle {role_id}")
        try:
            role = self.db.get_document(self.collection, role_id)
            
            print(f"[DEBUG] TaskManagerService.get_all_tasks - Document du rôle trouvé: {role}")
            
            if role and 'tasks' in role:
                tasks = role['tasks']
                print(f"[DEBUG] TaskManagerService.get_all_tasks - {len(tasks)} tâches trouvées")
                return tasks
            print("[DEBUG] TaskManagerService.get_all_tasks - Aucune tâche trouvée")
            return []
        except Exception as e:
            print(f"[ERROR] TaskManagerService.get_all_tasks - Erreur: {str(e)}")
            return []
        
    def create_task(self, role_id, task_data):
        """Crée une nouvelle tâche
        
        Args:
            role_id: ID du rôle auquel ajouter la tâche
            task_data: Dictionnaire contenant les données de la tâche :
                      - title: Titre de la tâche
                      - description: Description de la tâche
                      - module: Module associé
                      - icon: Icône de la tâche
        """
        print("[DEBUG] TaskManagerService.create_task - Création d'une nouvelle tâche")
        try:
            # Récupérer le rôle actuel
            role = self.db.get_document(self.collection, role_id)
            if not role:
                print(f"[ERROR] TaskManagerService.create_task - Rôle {role_id} non trouvé")
                return False
                
            # Initialiser la liste des tâches si elle n'existe pas
            if 'tasks' not in role:
                role['tasks'] = []
                
            # Ajouter la nouvelle tâche
            role['tasks'].append(task_data)
            
            # Mettre à jour le document
            self.db.update_document(self.collection, role_id, role)
            return True
            
        except Exception as e:
            print(f"[ERROR] TaskManagerService.create_task - Erreur: {str(e)}")
            return False
            
    def update_task(self, role_id, task_index, task_data):
        """Met à jour une tâche existante"""
        print("[DEBUG] TaskManagerService.update_task - Mise à jour d'une tâche")
        try:
            role = self.db.get_document(self.collection, role_id)
            if not role or 'tasks' not in role or task_index >= len(role['tasks']):
                return False
                
            role['tasks'][task_index] = task_data
            self.db.update_document(self.collection, role_id, role)
            return True
            
        except Exception as e:
            print(f"[ERROR] TaskManagerService.update_task - Erreur: {str(e)}")
            return False
            
    def delete_task(self, role_id, task_index):
        """Supprime une tâche"""
        print("[DEBUG] TaskManagerService.delete_task - Suppression d'une tâche")
        try:
            role = self.db.get_document(self.collection, role_id)
            if not role or 'tasks' not in role or task_index >= len(role['tasks']):
                return False
                
            role['tasks'].pop(task_index)
            self.db.update_document(self.collection, role_id, role)
            return True
            
        except Exception as e:
            print(f"[ERROR] TaskManagerService.delete_task - Erreur: {str(e)}")
            return False
