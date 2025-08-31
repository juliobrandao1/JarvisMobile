import os
os.environ['KIVY_LOG_LEVEL'] = 'debug'
os.environ['KIVY_IMAGE'] = 'pil,sdl2'  # força PIL para imagens (inclui GIF)
from openai import OpenAI
from google.cloud import texttospeech
from google.oauth2 import service_account
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
import google.generativeai as genai
import threading
import re
import time
import datetime
import pywhatkit
import pygame
import google.generativeai as genai
import speech_recognition as sr
import vertexai
from vertexai.preview.generative_models import GenerativeModel,ChatSession

# Caminhos restaurados para os ficheiros GIF originais
jarvis_gif_full_path =  os.path.join(os.path.dirname(__file__), "assets", "jarvis.gif")
onda_sonora_gif_full_path =  os.path.join(os.path.dirname(__file__), "assets", "wave.gif")
waiting_gif_full_path =  os.path.join(os.path.dirname(__file__), "assets", "waiting.gif")
# credencial cloud
credentials = service_account.Credentials.from_service_account_file(
    "C:/Users/Julio/Documents/PycharmProjects/JarvisProject3/json/key.json")
clientGoogle = texttospeech.TextToSpeechClient(credentials=credentials)
# beep
frequency = 300  # Set Frequency To 2500 Hertz
duration = 600  # Set Duration To 1000 ms == 1 second
# time
time.clock = time.time
# nome da IA
nome = "Jarvis"
jarvis = 0
# chave gemini
key = "AIzaSyDxAbYdnjk3lmyTrcWeQ4QZoBnhvTusKzA"
os.environ["GOOGLE_API_KEY"] = key
client = OpenAI(api_key=key)
genai.configure(api_key=key)
#answer
resp = "Inicializando Jarvis 4.0"


Window.clearcolor = (0.1, 0.1, 0.1, 1)

class JarvisLayout(BoxLayout):
    pass






def recordText(txt):
    arquivo_saida = "audio/saida.wav"
    synthesis_input = texttospeech.SynthesisInput(text=txt)
    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        name="pt-BR-Standard-B",  # Uma das vozes brasileiras da Google
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=1.4
    )

    response = clientGoogle.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(arquivo_saida, "wb") as out:
        out.write(response.audio_content)
    print(f"Áudio salvo: {arquivo_saida}")

    pygame.mixer.init()
    pygame.mixer.music.load('audio/saida.wav')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Encerra o mixer para liberar o arquivo
    pygame.mixer.music.stop()
    pygame.mixer.quit()


# CHAT IA
vertexai.init(project="vxgva1", location="us-central1")
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()



prompt = (
    'Jarvis, a partir de agora voce vai sempre tentar responder minhas perguntas de uma maneira objetiva , com poucas palavras, tentando não exceder 600 caracteres. Pode usar frases como: \'Ok, entendido!\' ou \'É pra já, voce que manda\' ou \'Vamos nessa!\'... Tente usar de vez em quando essas e algumas outras frases de efeito antes de responder as minhas perguntas ou executar as ações solicitadas.Sempre que a resposta for longa e não tiver jeito de encurta-la , utilize frases como: \'me de um momento pra pensar\' ou \'um momento, preciso pesquisar aqui rapidamente\' e outras frases para suprir o silencio até voce retornar com o que preciso. Voce pode incluir algumas piadas tambem, um pouco de humor com piadas de tiozao são sempre bem vindos. porem, não exagere.É imprescindivel voce responder com humor em 80% fazendo piadinhas . Lembre-se: humor em 80%. Incorpore esse padrão em todas as respostas!  Obedeça esses parametros em todas as respostas. Se todas as instruções foram recebidas e entendidas , responda apenas com: \'Inicialização Jarvis Concluída.\'')
# Prompt
a = model.start_chat().send_message(prompt)
print(a.text)
resp = a.text

def Response(query,jarvis):
    if len(query) > 4:
        if (jarvis != 0) or (("jarvis" or "jarvis" or "javis" or "jar") in query):
            jarvis = 5  # 5 beeps até precisar chamar novamente pelo nome
            # resp = api.send_message(query)
            query = query.replace("jarvis", "")
            # resp = chatGPT(query)
            resp = chatfun(chat, query)
            print(resp)
            resp = resp.replace("*", "")
            resp = re.sub(r'[^\w\s.,!?;:áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\'\"]+', '', resp)
            print(len(resp))
            if len(resp) < 600:
                recordText(resp)

            # speak("Algo mais em que eu possa te ajudar? ")

        else:
            print("ok")

    else:
        print("Hey Julio, não compreendi. pode repetir? ")
        jarvis = jarvis - 1


# gemini
def chatfun(chat: ChatSession, prompt: str) -> str:
    response = chat.send_message(prompt + " resume a resposta em no maximo 600 caracteres")
    return response.text

def wish():
    hour = int(datetime.datetime.now().hour)

    if hour > 6 and hour <= 12:
        # speak("good morning")
        recordText("Bom Dia")
    elif hour >= 12 and hour <= 18:
        # speak("good afternoon")
        recordText("Boa Tarde")
    elif hour >= 0 and hour <= 6:
        # speak("good afternoon")
        recordText("Boa Madrugada")
    else:
        # speak("good evening")
        recordText("Boa Noite")
    recordText(f"Sou {nome}, a seu comando. Como posso ser útil? ")



class JarvisApp(App):
    # Passa os caminhos completos para o Kivy
    jarvis_gif_path = StringProperty(jarvis_gif_full_path)
    onda_sonora_gif_path = StringProperty(onda_sonora_gif_full_path)
    primeiro = 0  # mudar pra 1 pra saudação
    query = ""
    is_processing = False

    def start_listen(self):
        r = sr.Recognizer()
        wait = True
        with sr.Microphone() as source:
            r.pause_threshold = 3
            print("Linstening...")
            try:
                audio = r.listen(source)
                if wait is False:
                    return "none"
            except Exception as e:
                return "none"
        query = r.recognize_google(audio, language='pt-BR').lower()
        Response(query,1)
        Clock.schedule_once(self.reset_ui)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_listening = False

    def build(self):
      return JarvisLayout()

    def toggle_listening(self):
        if self.is_processing:
            print("Aguarde, já estou processando um pedido.")
            return

        self.is_processing = True

        self.is_listening = not self.is_listening
        onda_sonora_widget = self.root.ids.onda_sonora
        mic_button_widget = self.root.ids.mic_button


        retorno =""
        if self.primeiro == 1:
            wish()
            self.primeiro = 0
        else:

            if self.is_listening:
                self.is_listening = not self.is_listening
                print("Microfone ATIVADO")
                onda_sonora_widget.anim_delay = 0.1
                onda_sonora_widget.opacity = 1
                mic_button_widget.text = "Ouvindo..."
                mic_button_widget.background_color = (0.8, 0.2, 0.2, 1)

                thread = threading.Thread(target=self.start_listen, daemon=True)
                thread.start()

    def reset_ui(self, dt=0):
        # Esta função é chamada pelo Clock e roda no thread principal, de forma segura.
        print("Microfone DESATIVADO e UI resetada.")
        onda_sonora_widget = self.root.ids.onda_sonora
        mic_button_widget = self.root.ids.mic_button

        mic_button_widget.text = "Aperte para falar"
        mic_button_widget.background_color = (0.2, 0.6, 0.8, 1)  # Cor original (exemplo)
        onda_sonora_widget.opacity = 0
        # Libera a flag para permitir um novo processamento
        self.is_processing = False



















if __name__ == '__main__':
     thread_tela = threading.Thread(target=JarvisApp().run(), daemon=True)
     thread_tela.start()


