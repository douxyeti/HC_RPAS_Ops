from app.services.firebase_service import FirebaseService
import unicodedata
import re

class RolesManagerService:
    """Service pour la gestion des rôles et leurs tâches"""
    
    def __init__(self):
        self.db = FirebaseService()
        self.collection = 'roles'
        
    def get_all_roles(self):
        """Récupère tous les rôles"""
        print("[DEBUG] RolesManagerService.get_all_roles - Début de la récupération")
        roles = self.db.get_collection(self.collection)
        print(f"[DEBUG] RolesManagerService.get_all_roles - Rôles bruts reçus de Firebase:")
        for role in roles:
            print(f"[DEBUG] RolesManagerService.get_all_roles - ID: '{role.get('id')}', Nom: '{role.get('name')}'")
        print(f"[DEBUG] RolesManagerService.get_all_roles - {len(roles)} rôles récupérés")
        for role in roles:
            print(f"[DEBUG] RolesManagerService.get_all_roles - Rôle: {role.get('id', 'NO_ID')}, Tâches: {len(role.get('tasks', []))}")
        return roles
        
    def get_role(self, role_id):
        """Récupère un rôle par son ID"""
        print(f"[DEBUG] RolesManagerService.get_role - Récupération du rôle {role_id}")
        # Essaie d'abord avec l'ID exact
        role = self.db.get_document(self.collection, role_id)
        if role:
            print(f"[DEBUG] RolesManagerService.get_role - Rôle trouvé avec {len(role.get('tasks', []))} tâches")
            return role
            
        # Si non trouvé, essaie avec l'ID normalisé
        normalized_id = self.normalize_string(role_id)
        print(f"[DEBUG] RolesManagerService.get_role - Essai avec l'ID normalisé: {normalized_id}")
        role = self.db.get_document(self.collection, normalized_id)
        if role:
            print(f"[DEBUG] RolesManagerService.get_role - Rôle trouvé avec ID normalisé, {len(role.get('tasks', []))} tâches")
        else:
            print(f"[DEBUG] RolesManagerService.get_role - Rôle non trouvé avec ID normalisé")
        return role
        
    def create_role(self, role_data):
        """Crée un nouveau rôle
        
        Args:
            role_data: Dictionnaire contenant les données du rôle :
                      - id: Identifiant unique du rôle
                      - name: Nom du rôle
                      - description: Description du rôle
                      - tasks: Liste des tâches associées
        """
        try:
            # Vérifie que l'ID est présent
            if 'id' not in role_data:
                print("Erreur: l'ID du rôle est requis")
                return False
                
            # Initialise la liste des tâches si elle n'existe pas
            if 'tasks' not in role_data:
                role_data['tasks'] = []
                
            # Utilise l'ID fourni pour créer le document
            if self.db.add_document_with_id(self.collection, role_data['id'], role_data):
                # Met à jour la liste des rôles disponibles dans l'application
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if hasattr(app, 'available_roles'):
                    app.available_roles.append(role_data['name'])
                    app.available_roles.sort()
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la création du rôle : {e}")
            return False
            
    def update_role(self, role_id, role_data):
        """Met à jour un rôle existant"""
        try:
            print(f"[DEBUG] RolesManagerService.update_role - Début mise à jour pour role_id: {role_id}")
            print(f"[DEBUG] RolesManagerService.update_role - Données reçues: {role_data}")
            
            if not role_id:
                print("[DEBUG] RolesManagerService.update_role - Erreur: ID manquant")
                return False
                
            old_role = self.get_role(role_id)
            if not old_role:
                print("[DEBUG] RolesManagerService.update_role - Erreur: Rôle non trouvé")
                return False
                
            print(f"[DEBUG] RolesManagerService.update_role - Ancien rôle: {old_role}")
            
            # Conserver l'ID et les champs existants si non fournis
            role_data['id'] = role_id
            if 'tasks' not in role_data and 'tasks' in old_role:
                role_data['tasks'] = old_role['tasks']
            if 'permissions' not in role_data and 'permissions' in old_role:
                role_data['permissions'] = old_role['permissions']
            
            if self.db.update_document(self.collection, role_id, role_data):
                # Met à jour la liste des rôles disponibles dans l'application
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if hasattr(app, 'available_roles') and old_role:
                    print(f"[DEBUG] RolesManagerService.update_role - available_roles avant: {app.available_roles}")
                    if old_role.get('name') in app.available_roles:
                        app.available_roles.remove(old_role.get('name'))
                    app.available_roles.append(role_data['name'])
                    app.available_roles.sort()
                    print(f"[DEBUG] RolesManagerService.update_role - available_roles après: {app.available_roles}")
                print("[DEBUG] RolesManagerService.update_role - Mise à jour réussie")
                return True
            print("[DEBUG] RolesManagerService.update_role - Échec de la mise à jour dans Firebase")
            return False
        except Exception as e:
            print(f"[DEBUG] RolesManagerService.update_role - Erreur: {e}")
            return False
            
    def delete_role(self, role_id):
        """Supprime un rôle"""
        try:
            # Empêche la suppression du rôle Super Admin
            if role_id == 'super_admin':
                print("[DEBUG] RolesManagerService.delete_role - Tentative de suppression du rôle Super Admin interdite")
                return False

            role = self.get_role(role_id)
            if self.db.delete_document(self.collection, role_id):
                # Met à jour la liste des rôles disponibles dans l'application
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if hasattr(app, 'available_roles') and role:
                    if role.get('name') in app.available_roles:
                        app.available_roles.remove(role.get('name'))
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la suppression du rôle : {e}")
            return False
            
    def get_role_tasks(self, role_id):
        """Récupère toutes les tâches d'un rôle
        
        Args:
            role_id: ID du rôle
            
        Returns:
            Liste des tâches du rôle ou liste vide si le rôle n'existe pas
        """
        role = self.get_role(role_id)
        if role and 'tasks' in role:
            return role['tasks']
        return []
        
    def add_task(self, role_id, task_data):
        """Ajoute une nouvelle tâche à un rôle
        
        Args:
            role_id: ID du rôle
            task_data: Dictionnaire contenant les données de la tâche :
                      - name: Nom de la tâche
                      - description: Description de la tâche
                      - module: Module associé (operations, maintenance, etc.)
                      - icon: Icône de la tâche
                      
        Returns:
            True si la tâche a été ajoutée avec succès, False sinon
        """
        try:
            role = self.get_role(role_id)
            if not role:
                return False
                
            # Initialise la liste des tâches si elle n'existe pas
            if 'tasks' not in role:
                role['tasks'] = []
                
            # Ajoute la nouvelle tâche
            role['tasks'].append(task_data)
            
            # Met à jour le rôle
            return self.update_role(role_id, role)
        except Exception as e:
            print(f"Erreur lors de l'ajout de la tâche : {e}")
            return False
            
    def update_task(self, role_id: str, task_index: int, task_data: dict) -> bool:
        """Met à jour une tâche existante pour un rôle donné.

        Args:
            role_id (str): L'ID du rôle
            task_index (int): L'index de la tâche à mettre à jour
            task_data (dict): Les nouvelles données de la tâche

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            # Récupérer le rôle
            role_ref = self.db.collection('roles').document(role_id)
            role = role_ref.get()
            
            if not role.exists:
                return False
            
            # Récupérer les données du rôle
            role_data = role.to_dict()
            
            # Vérifier que l'index est valide
            if 'tasks' not in role_data or task_index >= len(role_data['tasks']):
                return False
            
            # Mettre à jour la tâche
            role_data['tasks'][task_index] = task_data
            
            # Sauvegarder les modifications
            role_ref.update(role_data)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la tâche : {str(e)}")
            return False
            
    def delete_task(self, role_id, task_index):
        """Supprime une tâche
        
        Args:
            role_id: ID du rôle
            task_index: Index de la tâche à supprimer
            
        Returns:
            True si la tâche a été supprimée avec succès, False sinon
        """
        try:
            role = self.get_role(role_id)
            if not role or 'tasks' not in role or task_index >= len(role['tasks']):
                return False
                
            # Supprime la tâche
            role['tasks'].pop(task_index)
            
            # Met à jour le rôle
            return self.update_role(role_id, role)
        except Exception as e:
            print(f"Erreur lors de la suppression de la tâche : {e}")
            return False

    def get_all_tasks(self):
        """Récupère toutes les tâches de tous les rôles"""
        tasks = []
        try:
            roles = self.get_all_roles()
            for role in roles:
                role_tasks = role.get('tasks', [])
                for task in role_tasks:
                    if task not in tasks:  # Éviter les doublons
                        tasks.append(task)
            return tasks
        except Exception as e:
            print(f"Erreur lors de la récupération des tâches : {e}")
            return []

    def get_tasks_for_role(self, role_id):
        """Récupère les tâches pour un rôle spécifique"""
        role = self.get_role(role_id)
        return role.get('tasks', []) if role else []

    def add_task_to_role(self, role_id, task_data):
        """Ajoute une tâche à un rôle spécifique"""
        role = self.get_role(role_id)
        if role:
            tasks = role.get('tasks', [])
            task_data['id'] = str(len(tasks))  # ID simple basé sur l'index
            tasks.append(task_data)
            role['tasks'] = tasks
            self.update_role(role_id, role)
            return True
        return False

    def update_task_in_role(self, role_id, task_id, task_data):
        """Met à jour une tâche dans un rôle spécifique"""
        role = self.get_role(role_id)
        if role:
            tasks = role.get('tasks', [])
            for i, task in enumerate(tasks):
                if str(task.get('id', '')) == str(task_id):
                    task_data['id'] = task_id  # Préserver l'ID
                    tasks[i] = task_data
                    role['tasks'] = tasks
                    self.update_role(role_id, role)
                    return True
        return False

    def remove_task_from_role(self, role_id, task_id):
        """Supprime une tâche d'un rôle spécifique"""
        role = self.get_role(role_id)
        if role:
            tasks = role.get('tasks', [])
            tasks = [t for t in tasks if str(t.get('id', '')) != str(task_id)]
            role['tasks'] = tasks
            self.update_role(role_id, role)
            return True
        return False

    def create_task(self, task_data):
        """Crée une nouvelle tâche globale (non associée à un rôle)"""
        # Pour l'instant, stockons les tâches globales dans un rôle spécial
        role_id = 'global_tasks'
        role = self.get_role(role_id)
        if not role:
            role = {
                'id': role_id,
                'name': 'Tâches Globales',
                'tasks': []
            }
        tasks = role.get('tasks', [])
        task_data['id'] = str(len(tasks))
        tasks.append(task_data)
        role['tasks'] = tasks
        self.update_role(role_id, role)
        return True

    def update_task(self, task_id, task_data):
        """Met à jour une tâche globale"""
        role_id = 'global_tasks'
        return self.update_task_in_role(role_id, task_id, task_data)

    def delete_task(self, task_id):
        """Supprime une tâche globale"""
        role_id = 'global_tasks'
        return self.remove_task_from_role(role_id, task_id)

    def normalize_string(self, text):
        """Normalise une chaîne de caractères pour l'utiliser comme ID
        
        - Remplace les caractères accentués par leur équivalent non accentué
        - Remplace les espaces par des underscores
        - Supprime les caractères spéciaux
        - Met tout en minuscules
        """
        print(f"[DEBUG] RolesManagerService.normalize_string - Texte original: '{text}'")
        # Remplace les caractères accentués
        text_unaccented = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        print(f"[DEBUG] RolesManagerService.normalize_string - Après suppression accents: '{text_unaccented}'")
        # Met en minuscules
        text_lower = text_unaccented.lower()
        print(f"[DEBUG] RolesManagerService.normalize_string - Après minuscules: '{text_lower}'")
        # Remplace les espaces par des underscores et supprime les caractères spéciaux
        text_clean = re.sub(r'[^a-z0-9_]', '_', text_lower)
        print(f"[DEBUG] RolesManagerService.normalize_string - Après nettoyage: '{text_clean}'")
        # Remplace les underscores multiples par un seul
        text_single_underscore = re.sub(r'_+', '_', text_clean)
        # Supprime les underscores au début et à la fin
        text_final = text_single_underscore.strip('_')
        print(f"[DEBUG] RolesManagerService.normalize_string - Résultat final: '{text_final}'")
        return text_final
