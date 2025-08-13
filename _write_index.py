from app.services.firebase_service import FirebaseService
from app.utils.module_discovery import ModuleDiscovery
from app.utils.module_initializer import ModuleInitializer

fs = FirebaseService.get_instance()
mi = ModuleInitializer()
branch = getattr(mi, 'current_branch', '') or ''
md = ModuleDiscovery(fs)

# même algo que Discovery pour le nom de collection
coll = f'module_indexes_modules_{md._sanitize_branch_name(branch)}'

# modèle minimal (adapte selon ce que _sample_docs.py montre)
doc = {
    'id': f'module_{md._sanitize_branch_name(branch)}',
    'branch': branch,
    'type': 'core',
    'version': '1.0.1',
    'main_screen': 'dashboard',
    'description': f"Module principal pour la branche {branch}",
    'is_master': branch in ('master','RPAS_ops_master'),
}

# écriture avec l'ID = champ 'id'
fs.set_data_with_id(coll, doc['id'], doc)
print('WROTE', coll, doc['id'])

# vérif lecture
docs = fs.get_collection(coll) or []
print('VERIFY count =', len(docs))
for d in docs: print(d)
