import os, sys
# --- shim pour exécution directe (python modules/test_module/main.py) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import os, sys
# --- shim pour exécution directe (python modules/test_module/main.py) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from app.core.invocation_mixin import InvocationConsumerMixin
from app.services.firebase_service import FirebaseService

# --- Mode test local ---
TEST_LOCAL = False


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", spacing=16, padding=24)
        root.add_widget(Label(text="Test Module — Splash", halign="center"))
        btn = Button(text="Go to Dashboard", size_hint=(None, None), width=220, height=48)
        btn.bind(on_release=lambda *_: setattr(self.manager, "current", "dashboard"))
        root.add_widget(btn)
        self.add_widget(root)


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=24)
        root.add_widget(Label(text="Login (placeholder)", halign="center"))
        self.add_widget(root)


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = Label(text="Dashboard (en attente d’invocation)", halign="center")
        root = BoxLayout(orientation="vertical", padding=24)
        root.add_widget(self.status)
        self.add_widget(root)


class ModuleScreenManager(InvocationConsumerMixin, ScreenManager):
    MODULE_NAME = "test_module"
    ROUTE_ON_INVOCATION = "dashboard"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(DashboardScreen(name="dashboard"))

    def handle_invocation_params(self, params: dict) -> None:
        try:
            dash = self.get_screen("dashboard")
            dash.status.text = f"Params reçus: {params}"
        except Exception:
            pass

    def on_start(self):
        print("[INVOCATION] Mode Firebase réel (module)")
        try:
            from app.services.firebase_service import FirebaseService
        except Exception as e:
            print("[INVOCATION][ERROR] Firebase import failed:", e)
            return

        firebase_service = FirebaseService.get_instance()
        current_user_id = getattr(firebase_service, "current_user_id", None) or "unknown_user"
        print(f"[INVOCATION] will consume for user={current_user_id} module={self.MODULE_NAME}")

        inv = self.consume_invocation_for_self(firebase_service, current_user_id)
        print(f"[INVOCATION] consume result: {inv!r}")

        if not inv:
            print("[INVOCATION][WARN] no invocation found. Staying on current screen.")
        # (Optionnel si mixin a start_invocation_poll)
        # self.start_invocation_poll(firebase_service, current_user_id, interval=5.0)



class TestModuleApp(App):
    def build(self):
        return ModuleScreenManager()

    def on_start(self):
        if hasattr(self.root, "on_start"):
            self.root.on_start()


if __name__ == "__main__":
    TestModuleApp().run()

from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivy.properties import StringProperty

from app.core.invocation_mixin import InvocationConsumerMixin
from app.services.firebase_service import FirebaseService

# --- Mode test local ---
TEST_LOCAL = False

KV = """
<SplashScreen>:
    MDBoxLayout:
        orientation: "vertical"
        spacing: "16dp"
        padding: "24dp"
        MDLabel:
            text: "Test Module — Splash"
            halign: "center"
        MDRaisedButton:
            text: "Go to Dashboard"
            pos_hint: {"center_x": .5}
            on_release: app.root.current = "dashboard"

<LoginScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "24dp"
        MDLabel:
            text: "Login (placeholder)"
            halign: "center"

<DashboardScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "24dp"
        MDLabel:
            id: status
            text: root.status_text
            halign: "center"
"""

class SplashScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class DashboardScreen(Screen):
    status_text = StringProperty("Dashboard (en attente d’invocation)")

class ModuleScreenManager(InvocationConsumerMixin, MDScreenManager):
    MODULE_NAME = "test_module"
    ROUTE_ON_INVOCATION = "dashboard"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        # Ajoute les écrans de base
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(DashboardScreen(name="dashboard"))

    def handle_invocation_params(self, params: dict) -> None:
        # Appelé par le mixin quand des params d'invocation sont présents
        try:
            dash = self.get_screen("dashboard")
            dash.status_text = f"Params reçus: {params}"
        except Exception:
            pass

    def on_start(self):
        print("[INVOCATION] Mode Firebase réel (module)")
        try:
            from app.services.firebase_service import FirebaseService
        except Exception as e:
            print("[INVOCATION][ERROR] Firebase import failed:", e)
            return

        firebase_service = FirebaseService.get_instance()
        current_user_id = getattr(firebase_service, "current_user_id", None) or "unknown_user"
        print(f"[INVOCATION] will consume for user={current_user_id} module={self.MODULE_NAME}")

        inv = self.consume_invocation_for_self(firebase_service, current_user_id)
        print(f"[INVOCATION] consume result: {inv!r}")

        if not inv:
            print("[INVOCATION][WARN] no invocation found. Staying on current screen.")
        # (Optionnel si mixin a start_invocation_poll)
        # self.start_invocation_poll(firebase_service, current_user_id, interval=5.0)



class TestModuleApp(App):
    def build(self):
        Builder.load_string(KV)
        return ModuleScreenManager()

    def on_start(self):
        # Propager au ScreenManager s'il implémente on_start
        if hasattr(self.root, "on_start"):
            self.root.on_start()

if __name__ == "__main__":
    TestModuleApp().run()

from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import Screen, SlideTransition

from app.core.invocation_mixin import InvocationConsumerMixin
from app.services.firebase_service import FirebaseService

# --- Mode test local ---
TEST_LOCAL = False


# Écrans minimaux (widgets Kivy valides)
class SplashScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class DashboardScreen(Screen):
    pass


class ModuleScreenManager(InvocationConsumerMixin, MDScreenManager):
    MODULE_NAME = "test_module"
    ROUTE_ON_INVOCATION = "dashboard"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        # Ajoute les écrans de base
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(DashboardScreen(name="dashboard"))

    def handle_invocation_params(self, params: dict) -> None:
        # Hook appelé par le mixin quand des params d'invocation sont présents
        print(f"[test_module] params reçus: {params}")

    def on_start(self):
        if TEST_LOCAL:
            # Simulation d'une invocation entrante locale
            params = {"test_param": 123, "mode": "local"}
            print(f"[TEST_LOCAL] Consommation invocation: route='dashboard', params={params}")
            self._route_switch("dashboard")
            self._dispatch_params(params)
        else:
            # ----- Mode réel (exemple) -----
            # firebase_service = FirebaseService.get_instance()
            # current_user_id = getattr(firebase_service, "current_user_id", None) or "unknown_user"
            # self.consume_invocation_for_self(firebase_service, current_user_id)
            # --------------------------------
            pass


class TestModuleApp(App):
    def build(self):
        sm = ModuleScreenManager()
        return sm

    def on_start(self):
        # Propager au ScreenManager s'il implémente on_start
        if hasattr(self.root, "on_start"):
            self.root.on_start()


if __name__ == "__main__":
    TestModuleApp().run()
