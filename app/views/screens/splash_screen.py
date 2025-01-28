from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivymd.uix.button import MDButton, MDButtonText

class SplashScreen(MDScreen):
    progress = NumericProperty(0)
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        Clock.schedule_interval(self.update_progress, 0.05)
        
    def update_progress(self, dt):
        """Met à jour la barre de progression"""
        self.progress += 2
        if self.progress >= 100:
            # Arrête l'intervalle
            Clock.unschedule(self.update_progress)
            return False
        return True
        
    def switch_screen(self):
        """Change vers l'écran de login"""
        self.manager.current = "login"
