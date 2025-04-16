import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
from app.models.task import Task

# Créer une nouvelle tâche pour la gestion des procédures
new_task = {
    'title': 'Gestion des procédures',
    'description': 'Gérer les procédures et leurs étapes associées',
    'icon': 'clipboard-list',
    'module': 'operations',
    'screen': 'procedures_manager',
    'id': 'gestion_procedures'
}

# Récupérer le document super_admin
firebase = FirebaseService()
super_admin_doc = firebase.get_document('roles', 'super_admin')

# Ajouter la nouvelle tâche à la liste des tâches existantes
tasks = super_admin_doc.get('tasks', [])
tasks.append(new_task)

# Mettre à jour le document
firebase.update_document('roles', 'super_admin', {'tasks': tasks})

print("Tâche de gestion des procédures ajoutée avec succès")
