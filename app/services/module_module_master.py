# auto-generated registry (safe no-op)  module_master
def get_registry():
    class _Registry:
        def navigate_to_screen(self, screen_id, field_id=None, app=None, **kwargs):
            print(f"[REGISTRY module_master] navigate_to_screen -> screen_id={screen_id}, field_id={field_id}, kwargs={kwargs}")
            return True
    return _Registry()
