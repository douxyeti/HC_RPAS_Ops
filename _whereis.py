import inspect, textwrap
import app.utils.module_initializer as mi_mod
import app.utils.module_discovery as md_mod
from app.utils.module_initializer import ModuleInitializer
from app.utils.module_discovery import ModuleDiscovery

print('mi_mod file =', getattr(mi_mod, '__file__', None))
print('md_mod file =', getattr(md_mod, '__file__', None))
print('ModuleInitializer public methods =', [m for m in dir(ModuleInitializer) if not m.startswith('_')])
print('ModuleDiscovery  public methods =', [m for m in dir(ModuleDiscovery)  if not m.startswith('_')])

def dump(name, obj):
    try:
        src = textwrap.dedent(inspect.getsource(obj))
        print(f"\\n=== SOURCE {name} (first 2000 chars) ===\\n" + src[:2000])
    except Exception as e:
        print(f'cannot get source for {name}:', e)

dump('ModuleInitializer', ModuleInitializer)
dump('ModuleDiscovery',  ModuleDiscovery)
