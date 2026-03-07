import speech_recognition as sr
from gtts import gTTS
import os
import base64
from io import BytesIO


class AudioUtils:

    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._temp_file = 'temp_audio.wav'

    def converter_voz_para_texto(self, audio_bytes):
        try:
            with open(self._temp_file, 'wb') as f:
                f.write(audio_bytes)

            with sr.AudioFile(self._temp_file) as source:
                audio = self._recognizer.record(source)

            return self._recognizer.recognize_google(audio, language='en-US')

        except sr.UnknownValueError:
            return "Não foi possível entender o áudio"
        except sr.RequestError:
            return "Erro no serviço de reconhecimento de voz"
        except Exception as e:
            print(f"Erro na conversão de voz: {e}")
            return None
        finally:
            if os.path.exists(self._temp_file):
                os.remove(self._temp_file)

    def converter_texto_para_voz(self, texto, idioma='en'):
        try:
            tts = gTTS(text=texto, lang=idioma, slow=False)

            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)

            return base64.b64encode(audio_bytes.read()).decode('utf-8')

        except Exception as e:
            print(f"Erro na conversão texto-voz: {e}")
            return None
