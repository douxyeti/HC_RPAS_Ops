import inspect, textwrap
from app.utils.module_discovery import ModuleDiscovery

def dump(fn):
    try:
        print(f'\n=== {fn.__name__} ===\n' + textwrap.dedent(inspect.getsource(fn))[:4000])
    except Exception as e:
        print(f'ERR {fn.__name__}:', e)

dump(ModuleDiscovery.get_module_screens)
dump(ModuleDiscovery.get_screen_details)
dump(ModuleDiscovery.navigate_to_module_screen)
