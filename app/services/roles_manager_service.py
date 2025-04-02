from app.services.firebase_service import FirebaseService
import unicodedata
import re

class RolesManagerService:
    """Service pour l'accès aux données des rôles"""
    
    def __init__(self):
        """Initialise le service avec la connexion Firebase"""
        self.db = FirebaseService()
        self.collection = 'roles'
        
    def get_all_roles(self):
        """Récupère tous les rôles depuis Firebase
        
        Returns:
            list: Liste des rôles sous forme de dictionnaires
        """
        print("[DEBUG] RolesManagerService.get_all_roles - Début de la récupération")
        roles = self.db.get_collection(self.collection)
        
        # Debug logs
        print(f"[DEBUG] RolesManagerService.get_all_roles - Rôles bruts reçus de Firebase:")
        for role in roles:
            print(f"[DEBUG] RolesManagerService.get_all_roles - ID: '{role.get('id')}', Nom: '{role.get('name')}'")
        print(f"[DEBUG] RolesManagerService.get_all_roles - {len(roles)} rôles récupérés")
        for role in roles:
            print(f"[DEBUG] RolesManagerService.get_all_roles - Rôle: {role.get('id', 'NO_ID')}, Tâches: {len(role.get('tasks', []))}")
            
        return roles
        
    def get_role(self, role_id):
        """Récupère un rôle par son ID depuis Firebase
        
        Args:
            role_id (str): ID du rôle à récupérer
            
        Returns:
            dict: Données du rôle ou None si non trouvé
        """
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
        
    def get_role_by_name(self, role_name):
        """Récupère un rôle par son nom depuis Firebase
        
        Args:
            role_name (str): Nom du rôle à rechercher
            
        Returns:
            dict: Données du rôle ou None si non trouvé
        """
        print(f"[DEBUG] RolesManagerService.get_role_by_name - Recherche du rôle: {role_name}")
        
        # Récupérer tous les rôles
        roles = self.get_all_roles()
        
        # Normaliser le nom recherché
        normalized_name = self.normalize_string(role_name)
        print(f"[DEBUG] RolesManagerService.get_role_by_name - Nom normalisé: {normalized_name}")
        
        # Chercher le rôle correspondant
        for role in roles:
            role_normalized_name = self.normalize_string(role.get('name', ''))
            if role_normalized_name == normalized_name:
                print(f"[DEBUG] RolesManagerService.get_role_by_name - Rôle trouvé avec {len(role.get('tasks', []))} tâches")
                return role
                
        print(f"[DEBUG] RolesManagerService.get_role_by_name - Rôle non trouvé")
        return None
        
    def create_role(self, role_data):
        """Crée un nouveau rôle dans Firebase
        
        Args:
            role_data (dict): Données du rôle à créer
            
        Returns:
            dict: Données du rôle créé ou None en cas d'erreur
        """
        return self.db.create_document(self.collection, role_data)
        
    def update_role(self, role_id, role_data):
        """Met à jour un rôle existant dans Firebase
        
        Args:
            role_id (str): ID du rôle à mettre à jour
            role_data (dict): Nouvelles données du rôle
            
        Returns:
            dict: Données du rôle mis à jour ou None en cas d'erreur
        """
        return self.db.update_document(self.collection, role_id, role_data)
        
    def delete_role(self, role_id):
        """Supprime un rôle de Firebase
        
        Args:
            role_id (str): ID du rôle à supprimer
            
        Returns:
            bool: True si supprimé avec succès, False sinon
        """
        return self.db.delete_document(self.collection, role_id)
        
    @staticmethod
    def normalize_string(text):
        """Normalise une chaîne de caractères
        
        Args:
            text (str): Texte à normaliser
            
        Returns:
            str: Texte normalisé
        """
        if not text:
            return text
            
        print(f"[DEBUG] RolesManagerService.normalize_string - Texte original: '{text}'")
        
        # Supprimer les accents
        text_without_accents = ''.join(c for c in unicodedata.normalize('NFD', text)
                                      if unicodedata.category(c) != 'Mn')
        print(f"[DEBUG] RolesManagerService.normalize_string - Après suppression accents: '{text_without_accents}'")
        
        # Convertir en minuscules
        text_lower = text_without_accents.lower()
        print(f"[DEBUG] RolesManagerService.normalize_string - Après minuscules: '{text_lower}'")
        
        # Remplacer les espaces par des underscores et supprimer les caractères spéciaux
        text_clean = re.sub(r'[^a-z0-9_]', '_', text_lower)
        print(f"[DEBUG] RolesManagerService.normalize_string - Après nettoyage: '{text_clean}'")
        
        # Supprimer les underscores multiples
        text_final = re.sub(r'_+', '_', text_clean)
        print(f"[DEBUG] RolesManagerService.normalize_string - Résultat final: '{text_final}'")
        
        return text_final
