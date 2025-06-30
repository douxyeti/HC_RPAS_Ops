import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.services.firebase_service import FirebaseService

def setup_super_admin():
    """
    Creates the user document in the 'pilots' collection to link the auth UID
    to the user's data and role.
    """
    user_id = "Ta5xjw6gsShzoaXNYS5SriTkbAi2"
    user_data = {
        "first_name": "Mario",
        "last_name": "Boulet",
        "role_name": "Super administrateur"  # The role assigned to the user
    }

    print(f"Initializing Firebase Service for restored project...")
    # Ensure gcloud is configured to 'highcloud-rpas-ecosystem-86a4f'
    try:
        firebase_service = FirebaseService()
        db = firebase_service.db
        print("Firebase Service initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return

    print(f"\n--- Creating document for user ID: {user_id} ---")
    try:
        pilot_ref = db.collection('pilots').document(user_id)
        pilot_ref.set(user_data)
        print("Document created successfully in 'pilots' collection.")
        print(f"  ID: {user_id}")
        print(f"  Data: {user_data}")
    except Exception as e:
        print(f"An error occurred while creating the document: {e}")

    print("\n--- Setup complete ---")

if __name__ == "__main__":
    setup_super_admin()
