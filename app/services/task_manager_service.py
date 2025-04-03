from app.services.firebase_service import FirebaseService
from app.services.config_service import ConfigService

class TaskManagerService:
    """Service pour la gestion des tâches"""
    
    def __init__(self, firebase_service):
        print("[DEBUG] TaskManagerService.__init__ - Initialisation du service")
        self.db = firebase_service
        self.collection = 'roles'
        self.config_service = ConfigService()
        
    def get_role_by_name(self, role_name):
        """Récupère un rôle par son nom"""
        print(f"[DEBUG] TaskManagerService.get_role_by_name - Recherche du rôle '{role_name}'")
        try:
            # Table de correspondance des noms affichés vers les IDs
            name_to_id = {
                'Agent de sécurité': 'safety_officer',
                'Chef pilote': '1739113171349',
                'Commandant de bord': 'commandant_de_bord_20250209154602797597_7549',
                'Coordinateur des opérations': 'coordinateur_des_op_rations_20250209154602583657_7089',
                'Copilote': 'copilote_20250209154601638980_4466',
                'Examinateur': 'examinateur_20250209154601788307_4150',
                'Formateur': 'formateur_20250209154601869007_5483',
                'Gestionnaire des activités de maintenance': 'gestionnaire_des_activit_s_de_maintenance_20250209154602333301_9261',
                'Gestionnaire du cadre documentaire': 'gestionnaire_du_cadre_documentaire_20250209154601714872_5632',
                'Inspecteur': 'inspecteur_20250209154602148559_9165',
                'Instructeur': 'instructeur_20250209154602241623_4510',
                'Observateur au sol': 'observateur_au_sol_20250209154601953352_1681',
                'Opérateur de charge utile': 'op_rateur_de_charge_utile_20250209154602653054_5709',
                'Opérateur de station au sol': 'op_rateur_de_station_au_sol_20250209154602044502_4150',
                'Pilote': 'pilote_20250209154602727105_6859',
                'Pilote aux commandes': 'pilot_controls',
                'Responsable assurance de la qualité': 'quality_manager',
                'Responsable des opérations': 'ops_manager',
                'Spécialiste de mission': 'sp_cialiste_de_mission_20250209154602497849_6798',
                'Super Administrateur': 'super_admin',
                'Technicien Maintenance': 'technicien_maintenance_20250209154602418833_9484'
            }
            
            # Récupérer l'ID correspondant au nom affiché
            role_id = name_to_id.get(role_name)
            if not role_id:
                print(f"[DEBUG] TaskManagerService.get_role_by_name - Aucun ID trouvé pour le rôle '{role_name}'")
                return None
                
            print(f"[DEBUG] TaskManagerService.get_role_by_name - ID trouvé pour le rôle '{role_name}' : {role_id}")
                
            # Récupérer le rôle par son ID
            roles = self.db.get_collection(self.collection)
            print(f"[DEBUG] TaskManagerService.get_role_by_name - {len(roles)} rôles trouvés dans la collection")
            
            # Afficher tous les rôles pour le débogage
            print("[DEBUG] TaskManagerService.get_role_by_name - Rôles disponibles :")
            for r in roles:
                print(f"- {r.get('name')} (id: {r.get('id')})")
            
            role = next((r for r in roles if r.get('id') == role_id), None)
            
            if role:
                print(f"[DEBUG] TaskManagerService.get_role_by_name - Rôle trouvé avec l'ID {role_id}")
                print(f"[DEBUG] TaskManagerService.get_role_by_name - Données du rôle : {role}")
            else:
                print(f"[DEBUG] TaskManagerService.get_role_by_name - Aucun rôle trouvé avec l'ID {role_id}")
            
            return role
        except Exception as e:
            print(f"[ERROR] TaskManagerService.get_role_by_name - Erreur: {str(e)}")
            return None

    def get_fixed_tasks(self, role_name):
        """Récupère les tâches fixes depuis config.json pour un rôle donné"""
        print(f"[DEBUG] TaskManagerService.get_fixed_tasks - Recherche des tâches fixes pour {role_name}")
        try:
            # Convertir le nom du rôle en format snake_case pour config.json
            role_key = role_name.lower().replace(' ', '_')
            config_path = f'interface.roles.{role_key}.tasks'
            
            # Récupérer les tâches depuis config.json
            tasks = self.config_service.get_config(config_path)
            if tasks:
                # Marquer ces tâches comme fixes
                for task in tasks:
                    task['is_fixed'] = True
                print(f"[DEBUG] TaskManagerService.get_fixed_tasks - {len(tasks)} tâches fixes trouvées")
                return tasks
            return []
        except Exception as e:
            print(f"[ERROR] TaskManagerService.get_fixed_tasks - Erreur: {str(e)}")
            return []
        
    def get_all_tasks(self, role_id):
        """Récupère toutes les tâches d'un rôle (fixes et dynamiques)"""
        print(f"[DEBUG] TaskManagerService.get_all_tasks - Récupération des tâches pour le rôle {role_id}")
        try:
            all_tasks = []
            
            # 1. Récupérer le rôle depuis Firebase
            role = self.db.get_document(self.collection, role_id)
            if role:
                # 2. Récupérer les tâches fixes si c'est le Super Administrateur
                if role.get('name') == 'Super Administrateur':
                    fixed_tasks = self.get_fixed_tasks('Super Administrateur')
                    all_tasks.extend(fixed_tasks)
                    print(f"[DEBUG] TaskManagerService.get_all_tasks - {len(fixed_tasks)} tâches fixes ajoutées")
                
                # 3. Ajouter les tâches dynamiques de Firebase
                if 'tasks' in role:
                    # Marquer ces tâches comme non fixes
                    dynamic_tasks = role['tasks']
                    for task in dynamic_tasks:
                        task['is_fixed'] = False
                    all_tasks.extend(dynamic_tasks)
                    print(f"[DEBUG] TaskManagerService.get_all_tasks - {len(dynamic_tasks)} tâches dynamiques ajoutées")
                
            print(f"[DEBUG] TaskManagerService.get_all_tasks - Total: {len(all_tasks)} tâches")
            return all_tasks
            
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
                
            # Vérifier si c'est une tâche fixe
            if role.get('name') == 'Super Administrateur':
                fixed_tasks = self.get_fixed_tasks('Super Administrateur')
                if task_index < len(fixed_tasks):
                    print("[ERROR] TaskManagerService.update_task - Impossible de modifier une tâche fixe")
                    return False
                    
            role['tasks'][task_index - len(fixed_tasks)] = task_data
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
            if not role or 'tasks' not in role:
                return False
                
            # Vérifier si c'est une tâche fixe pour le Super Administrateur
            if role.get('name') == 'Super Administrateur':
                fixed_tasks = self.get_fixed_tasks('Super Administrateur')
                if task_index < len(fixed_tasks):
                    print("[ERROR] TaskManagerService.delete_task - Impossible de supprimer une tâche fixe")
                    return False
                # Ajuster l'index pour les tâches dynamiques
                task_index = task_index - len(fixed_tasks)
                
            if task_index >= len(role['tasks']):
                return False
                
            role['tasks'].pop(task_index)
            self.db.update_document(self.collection, role_id, role)
            return True
            
        except Exception as e:
            print(f"[ERROR] TaskManagerService.delete_task - Erreur: {str(e)}")
            return False
