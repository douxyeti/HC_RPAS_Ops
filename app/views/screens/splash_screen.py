from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.properties import NumericProperty

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
            # Change d'écran après un court délai
            Clock.schedule_once(self.switch_screen, 0.5)
            return False
        return True
        
    def switch_screen(self, dt):
        """Change vers l'écran principal"""
        # Pour le moment, nous n'avons pas d'autre écran
        pass
