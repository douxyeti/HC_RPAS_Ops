import inspect, textwrap
import app.utils.module_discovery as md_mod
src = textwrap.dedent(inspect.getsource(md_mod.ModuleDiscovery.navigate_to_module_screen))
print(src)
