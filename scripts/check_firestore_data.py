import os
import sys
from pathlib import Path

# Add the project root to the Python path to allow importing app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.services.firebase_service import FirebaseService

def check_firestore_data():
    """
    Connects to Firestore and inspects the 'users' collection.
    """
    print("Initializing Firebase Service...")
    try:
        # Initialize the service which handles Firebase connection
        firebase_service = FirebaseService()
        db = firebase_service.db
        print("Firebase Service initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Please ensure your GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly.")
        return

    print("\n--- Checking 'users' collection ---")
    users_ref = db.collection('users')
    users = users_ref.stream()

    user_count = 0
    for user_doc in users:
        user_count += 1
        print(f"\n[User Document ID]: {user_doc.id}")
        print(f"  Data: {user_doc.to_dict()}")

        print(f"  --- Checking 'roles' subcollection for user {user_doc.id} ---")
        roles_ref = user_doc.reference.collection('roles')
        roles = roles_ref.stream()
        
        role_count = 0
        for role_doc in roles:
            role_count += 1
            print(f"    [Role Document ID]: {role_doc.id}")
            print(f"      Data: {role_doc.to_dict()}")
        
        if role_count == 0:
            print("    No roles found in subcollection.")

    if user_count == 0:
        print("The 'users' collection is empty.")

    print("\n--- Check complete ---")

if __name__ == "__main__":
    check_firestore_data()
