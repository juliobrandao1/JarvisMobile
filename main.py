import os
os.environ['KIVY_LOG_LEVEL'] = 'debug'
os.environ['KIVY_IMAGE'] = 'pil,sdl2'  # força PIL para imagens (inclui GIF)

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window



# Caminhos restaurados para os ficheiros GIF originais
jarvis_gif_full_path =  os.path.join(os.path.dirname(__file__), "assets", "jarvis.gif")
onda_sonora_gif_full_path =  os.path.join(os.path.dirname(__file__), "assets", "wave.gif")
waiting_gif_full_path =  os.path.join(os.path.dirname(__file__), "assets", "waiting.gif")

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class JarvisLayout(BoxLayout):
    pass

class JarvisApp(App):
    # Passa os caminhos completos para o Kivy
    jarvis_gif_path = StringProperty(jarvis_gif_full_path)
    onda_sonora_gif_path = StringProperty(onda_sonora_gif_full_path)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_listening = False

    def build(self):
        return JarvisLayout()

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        onda_sonora_widget = self.root.ids.onda_sonora
        mic_button_widget = self.root.ids.mic_button
        if self.is_listening:
            print("Microfone ATIVADO")
            onda_sonora_widget.anim_delay = 0.1
            onda_sonora_widget.opacity = 1
            mic_button_widget.text = "Ouvindo..."
            mic_button_widget.background_color = (0.8, 0.2, 0.2, 1)
        else:
            print("Microfone DESATIVADO")
            onda_sonora_widget.anim_delay = -1
            onda_sonora_widget.opacity = 0
            mic_button_widget.text = "Toque para Falar"
            mic_button_widget.background_color = (0.2, 0.6, 0.8, 1)

if __name__ == '__main__':
    JarvisApp().run()

