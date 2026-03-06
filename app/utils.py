import speech_recognition as sr
from gtts import gTTS
import os
import base64
import re
from io import BytesIO

class AudioUtils:
    
    @staticmethod
    def converter_voz_para_texto(audio_bytes):
        """
        Converte áudio em bytes para texto usando speech_recognition
        """
        recognizer = sr.Recognizer()
        temp_file = 'temp_audio.wav'
        
        try:
            # Salvar bytes temporariamente
            with open(temp_file, 'wb') as f:
                f.write(audio_bytes)
            
            # Carregar arquivo e converter
            with sr.AudioFile(temp_file) as source:
                audio = recognizer.record(source)
                
            # Reconhecer usando Google Speech Recognition
            texto = recognizer.recognize_google(audio, language='en-US')
            
            return texto
            
        except sr.UnknownValueError:
            return "Não foi possível entender o áudio"
        except sr.RequestError:
            return "Erro no serviço de reconhecimento de voz"
        except Exception as e:
            print(f"Erro na conversão de voz: {e}")
            return None
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    @staticmethod
    def converter_texto_para_voz(texto, idioma='en'):
        """
        Converte texto para áudio usando gTTS e retorna base64
        """
        try:
            tts = gTTS(text=texto, lang=idioma, slow=False)
            
            # Salvar em BytesIO
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            # Converter para base64
            audio_base64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
            
            return audio_base64
            
        except Exception as e:
            print(f"Erro na conversão texto-voz: {e}")
            return None

class ValidacaoUtils:
    
    @staticmethod
    def validar_email(email):
        """Valida formato de email"""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def validar_senha(senha):
        """Valida força da senha (mínimo 6 caracteres)"""
        return len(senha) >= 6
    
    @staticmethod
    def validar_nome(nome):
        """Valida nome (mínimo 3 caracteres)"""
        return len(nome.strip()) >= 3