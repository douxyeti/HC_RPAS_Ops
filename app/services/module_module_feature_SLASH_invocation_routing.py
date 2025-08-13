# auto-generated registry (safe no-op)
def get_registry():
    class _Registry:
        def navigate_to_screen(self, screen_id, field_id=None, app=None, **kwargs):
            print(f"[REGISTRY] navigate_to_screen -> screen_id={screen_id}, field_id={field_id}, kwargs={kwargs}")
            # Ici tu peux brancher la vraie nav si tu le souhaites (app.root, ScreenManager, etc.)
            return True
    return _Registry()
