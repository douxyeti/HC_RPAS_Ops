import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.services.firebase_service import FirebaseService

def inspect_roles_collection():
    """
    Connects to Firestore and inspects the 'roles' collection.
    """
    print("Initializing Firebase Service for restored project...")
    # This will use the gcloud config, which should be set to 'highcloud-rpas-ecosystem-86a4f'
    try:
        firebase_service = FirebaseService()
        db = firebase_service.db
        print("Firebase Service initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return

    print("\n--- Inspecting 'roles' collection (limit 5 documents) ---")
    roles_ref = db.collection('roles')
    docs = roles_ref.limit(5).stream()

    doc_count = 0
    for doc in docs:
        doc_count += 1
        print(f"\n[Document ID]: {doc.id}")
        print(f"  Data: {doc.to_dict()}")

    if doc_count == 0:
        print("The 'roles' collection is empty or could not be read.")

    print("\n--- Inspection complete ---")

if __name__ == "__main__":
    inspect_roles_collection()
