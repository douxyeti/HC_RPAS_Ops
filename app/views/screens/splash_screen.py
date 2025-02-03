from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty

class SplashScreen(MDScreen):
    progress = NumericProperty(0)
    loading_complete = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        Clock.schedule_once(self.start_progress, 0.5)
        
    def start_progress(self, dt):
        """Démarre la barre de progression"""
        Clock.schedule_interval(self.update_progress, 0.05)
        
    def update_progress(self, dt):
        """Met à jour la barre de progression"""
        if self.progress < 100:
            self.progress += 2
            self.ids.progress_bar.value = self.progress
            return True
        else:
            print("Progress reached 100%")
            self.loading_complete = True
            self.ids.status_label.text = "Cliquez pour continuer"
            self.ids.continue_button.disabled = False
            return False
            
    def go_to_login(self):
        """Passe à l'écran de connexion"""
        if self.loading_complete:
            print("go_to_login called")
            self.manager.current = "login"
