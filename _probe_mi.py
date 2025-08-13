from pprint import pprint
import traceback
from app.utils.module_initializer import get_module_initializer, ModuleInitializer

try:
    obj = get_module_initializer()
except Exception as e:
    print('get_module_initializer raised:', repr(e))
    traceback.print_exc()
    obj = None

print('OBJ =', obj)
print('TYPE =', type(obj))

def has(o, name):
    try:
        print(f'hasattr(obj, {name!r}) ->', hasattr(o, name))
    except Exception as e:
        print(f'hasattr error for {name}:', e)

if obj is not None:
    for name in ('initialize_with_services','initialize','run_indexation','build_index','build','run'):
        has(obj, name)

print('ModuleInitializer class methods (subset):', [a for a in dir(ModuleInitializer) if 'init' in a or 'index' in a])
