from app.services.firebase_service import FirebaseService
fs = FirebaseService.get_instance()

for coll in ('module_indexes_modules_master','module_indexes_modules_RPAS_ops_master'):
    try:
        docs = fs.get_collection(coll) or []
        print('COLL', coll, 'count', len(docs))
        for d in docs:
            print(d)
    except Exception as e:
        print('ERR', coll, e)
