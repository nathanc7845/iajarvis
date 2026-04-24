# -*- coding: utf-8 -*-
import speech_recognition as sr
import subprocess
import sys
import asyncio
import edge_tts
import tempfile
import os
import random
import webbrowser
import pyautogui
import time
import requests
import wikipedia
import feedparser
import threading
import keyboard
import urllib.parse

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import eel

# ==========================================
# CONFIGURAÇÕES (O PODER FINAL)
# ==========================================
# A chave que vai destrancar o mundo após o faturamento estar ativo
GEMINI_API_KEY = "" 

# Os links EXATOS (Certifique-se de "Ativar/Enable" eles no site do Sequematic!)
URL_LUZ_LIGAR = "https://sequematic.com/trigger-custom-webhook/CD70A2C386/164100"
URL_LUZ_DESLIGAR = "https://sequematic.com/trigger-custom-webhook/CD70A2C386/164102"

wikipedia.set_lang("pt")

class Jarvis:
    def __init__(self, microphone_index=None, voice="pt-BR-FranciscaNeural"):
        self.recognizer = sr.Recognizer()
        self.muted = False 
        self.microphone = sr.Microphone(device_index=microphone_index) if microphone_index is not None else sr.Microphone()
        self.voice = voice
        
        print("=" * 50)
        print("JARVIS MARK VIII - MODO VIP")
        print("=" * 50)
        self.falar("Estou a sua disposição, Senhor")

    async def _speak_async(self, texto):
        communicate = edge_tts.Communicate(texto, self.voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_name = tmp.name
        await communicate.save(tmp_name)
        return tmp_name

    def falar(self, texto):
        print(f"JARVIS: {texto}")
        try: eel.update_jarvis_speech(texto)
        except: pass
        try:
            tmp_file = asyncio.run(self._speak_async(texto))
            import pygame
            if not pygame.mixer.get_init(): pygame.mixer.init()
            pygame.mixer.music.load(tmp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if keyboard.is_pressed('space'):
                    pygame.mixer.music.stop()
                    break 
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            try: os.unlink(tmp_file)
            except: pass
        except Exception as e: print(f"Erro ao falar: {e}")

    def ouvir(self):
        try:
            with self.microphone as source:
                status = "[MUDO]" if self.muted else "[OUVINDO]"
                print(f"\n{status} Aguardando...")
                try: eel.update_status("Ouvindo...")
                except: pass
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
            texto = self.recognizer.recognize_google(audio, language='pt-BR')
            print(f"Você: {texto}")
            try: 
                eel.update_status("Processando...")
                eel.update_transcription(texto)
            except: pass
            return texto
        except: 
            try: eel.update_status("ONLINE")()
            except: pass
            return None

    def chamar_ia(self, pergunta):
        """Acesso direto à veia do Gemini (Modelo 2.5 Flash VIP)"""
        # A MÁGICA FINAL: Usando o modelo poderoso que está na sua lista!
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": f"Você é o Jarvis, assistente do Caleb. Responda de forma curta e direta: {pergunta}"}]}]
        }
        try:
            res = requests.post(url, headers=headers, json=data, timeout=10)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"ERRO IA (Código {res.status_code}): {res.text}")
                return "Meus servidores estão enfrentando turbulência."
        except Exception as e:
            print(f"ERRO CONEXÃO IA: {e}")
            return "Estou sem acesso à rede no momento."

    def controlar_luz(self, url):
        """Fingindo ser um humano para acender a luz"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            res = requests.get(url, headers=headers, timeout=5)
            # Se a sequência estiver ativada no site, vai dar HTTP 200!
            print(f"LOG LUZ: HTTP {res.status_code}")
            return res.status_code == 200
        except: return False

    def processar(self, comando):
        comando_lower = comando.lower()

        # MUTE
        if 'desmute' in comando_lower:
            self.muted = False; return "Escuta reativada."
        if 'mute' in comando_lower or 'silenciar' in comando_lower:
            self.muted = True; return "Em modo de espera."
        if self.muted: return None

        # SAUDAÇÕES
        if any(p in comando_lower for p in ['oi', 'olá', 'tudo bem']) and len(comando_lower.split()) <= 3:
            return "Tudo pronto, Caleb. Pode mandar."

        # LUZ
        elif 'acender luz' in comando_lower or 'ligar a luz' in comando_lower:
            if self.controlar_luz(URL_LUZ_LIGAR): return "Luzes acesas."
            return "Sinal bloqueado."

        elif 'apagar luz' in comando_lower or 'desligar a luz' in comando_lower:
            if self.controlar_luz(URL_LUZ_DESLIGAR): return "Tudo no escuro."
            return "Sinal bloqueado."

        # WHATSAPP
        elif 'mensagem para' in comando_lower:
            agenda = {"mamãe": "5531995036636", "nathan": "5531971673929", "nina": "5531996538173", "giovanna": "5531972010846", "ronald": "5531984725506"}
            if 'dizendo' in comando_lower:
                p1, msg = comando_lower.split('dizendo', 1)
                for nome, num in agenda.items():
                    if nome in p1:
                        webbrowser.open(f"whatsapp://send?phone={num}&text={urllib.parse.quote(msg)}")
                        time.sleep(1)
                        pyautogui.press('enter')
                        return f"Mensagem para {nome} enviada."
            return "Contato não encontrado."
        
        # YOUTUBE E MÚSICA
        elif 'abrir youtube' in comando_lower:
            webbrowser.open('https://www.youtube.com')
            return "Abrindo o YouTube."
            
        elif 'tocar' in comando_lower:
            musica = comando_lower.replace('tocar', '').strip()
            if musica:
                self.falar(f"Sintonizando {musica}.")
                
                # 1. Abre o app de forma direta
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write('YouTube Music')
                time.sleep(0.5)
                pyautogui.press('enter')
                
                # 2. Espera agressiva mas com garantia de foco
                # Ajustei para 7 segundos - tempo médio para o logo sumir e o app carregar
                time.sleep(7) 
                
                # 3. O PULO DO GATO: Alt+Tab rápido ou Clique de Foco
                # Isso garante que o comando '/' vá para dentro do app e não para o desktop
                pyautogui.click(960, 540) # Clique no centro
                time.sleep(0.5)
                
                # 4. Tenta a pesquisa (Mandei um ESC antes caso tenha algum pop-up na frente)
                pyautogui.press('esc')
                time.sleep(0.3)
                pyautogui.press('/')
                
                # 5. Digita a música (tirei o interval para ser instantâneo)
                time.sleep(0.5)
                pyautogui.write(musica)
                pyautogui.press('enter')
                
                # 6. Espera os resultados (3 segundos é o ideal para o layout carregar)
                time.sleep(3)
                
                # 7. Sniper
                pyautogui.click(592, 456)
                
                return None
            else:
                return "O que você quer que eu toque, senhor?"
            
            # CONTROLE DE MÍDIA (PLAY/PAUSE/PROXIMA)
        elif 'pausar' in comando_lower or 'despausar' in comando_lower or 'play' in comando_lower:
            pyautogui.press('playpause')
            return "Reprodução alterada."
            
        elif 'próxima música' in comando_lower or 'pular' in comando_lower:
            pyautogui.press('nexttrack')
            return "Pulando faixa."
            
        elif 'voltar música' in comando_lower or 'faixa anterior' in comando_lower:
            pyautogui.press('prevtrack')
            return "Voltando a faixa."

       # 5. SISTEMA
        elif 'abrir explorer' in comando_lower:
            os.system('explorer'); return "Arquivos abertos."
        elif 'abrir navegador' in comando_lower:
            # Caminho absoluto para forçar a abertura do Opera GX puro
            os.system(r'start "" "%LocalAppData%\Programs\Opera GX\opera.exe"')
            return "Navegador pronto."
        # VOLUME
        elif 'volume' in comando_lower:
            try:
                import comtypes
                comtypes.CoInitialize()
                lvl = [int(s) for s in comando_lower.split() if s.isdigit()][0]
                devices = AudioUtilities.GetSpeakers()
                try: interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                except: interface = devices.EndpointVolume
                vol = cast(interface, POINTER(IAudioEndpointVolume))
                vol.SetMasterVolumeLevelScalar(lvl / 100.0, None)
                return f"Volume em {lvl}%."
            except: return "Erro no áudio."

        # ENCERRAMENTO
        elif 'desligar computador' in comando_lower or 'desligar pc' in comando_lower:
            self.falar("Iniciando encerramento do computador em 5 segundos."); os.system("shutdown /s /t 5"); return None
        elif 'cancelar desligamento' in comando_lower:
            os.system("shutdown /a"); return "Desligamento abortado."
        elif 'desligar jarvis' in comando_lower or 'encerrar sistema' in comando_lower:
            self.falar("Desconectando. Até logo."); sys.exit(0)

        # IA
        else:
            return self.chamar_ia(comando)

    def executar(self):
        while True:
            texto = self.ouvir()
            if texto:
                resposta = self.processar(texto)
                if resposta: self.falar(resposta)
            try: eel.update_status("ONLINE")
            except: pass

if __name__ == "__main__":
    eel.init('web')
    jarvis = Jarvis(microphone_index=1)
    
    @eel.expose
    def comando_manual(comando):
        print(f"\n[MANUAL] Você: {comando}")
        resposta = jarvis.processar(comando)
        if resposta: 
            jarvis.falar(resposta)

    thread = threading.Thread(target=jarvis.executar, daemon=True)
    thread.start()
    
    try:
        print("Tentando abrir com Edge...")
        eel.start('index.html', size=(1024, 768), mode='edge')
    except Exception as e:
        import traceback
        print(f"Erro ao abrir com Edge: {e}")
        traceback.print_exc()
        try:
            print("Tentando abrir com navegador padrão...")
            eel.start('index.html', size=(1024, 768), mode='default')
        except Exception as ex:
            print(f"Erro fatal ao abrir navegador: {ex}")
            traceback.print_exc()