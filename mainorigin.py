import pygetwindow as gw
import tkinter as tk
import subprocess
import pyautogui
import time
import re
import json
import threading
from pygetwindow import PyGetWindowException
from tkinter import simpledialog
from classic.janela import ajustar_janela
from classic.janela import esperar_todas_janelas
from classic.regHive import restaurar_reg_hive
from classic.vitoria import processar_vitoria_origin
from classic.janela import is_window_384x270
from classic.shared import lock, ocupacao_grid

SANDBOXIE_PATH = r"C:\Program Files\Sandboxie\Start.exe"
GAME_PATH = r"C:\Program Files\Axie Infinity - Origins\AxieInfinity-Origins.exe"
IMAGE_PATH = r"img/origin"
REGHIVE_PATH = r"C:\Sandbox"
FILA_PATH = 'contas-origin.json'

fila = []
fila_lock = threading.Lock()
processos_abertos = []
queued_sandboxes = []
num_total_sandboxes = 0
threads = []

def carregar_vencedores():
    try:
        with open(FILA_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def iniciar_bot():
    global queued_sandboxes

    entrada = simpledialog.askstring("Input", "Quantas sandboxes você tem? (Exemplo: '15' ou '15-30')")
    num_running_sandboxes = int(simpledialog.askinteger("Input", "Quantas sandboxes você quer rodar por vez?", minvalue=1))

    sandboxes_vencedoras = carregar_vencedores()

    if '-' in entrada:
        match = re.match(r'(\d+)-(\d+)', entrada)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            total_sandboxes = [str(i) for i in range(start, end + 1)]
        else:
            print("Entrada inválida. Exemplo de entrada válida: '15' ou '15-30'.")
            exit()
    else:
        num_total_sandboxes = int(entrada)
        total_sandboxes = [str(i + 1) for i in range(num_total_sandboxes)]

    # Removemos as vencedoras da lista
    total_sandboxes = [sb for sb in total_sandboxes if sb not in sandboxes_vencedoras]
    queued_sandboxes = total_sandboxes[num_running_sandboxes:]

    # Abrir as primeiras sandboxes
    for sandbox in total_sandboxes[:num_running_sandboxes]:
        t = threading.Thread(target=start_game_in_sandbox, args=(sandbox,))
        threads.append(t)
        t.start()

    if esperar_todas_janelas(num_running_sandboxes, 60, False):
        time.sleep(5)
        while True:
            jogar_origin()
            
def start_game_in_sandbox(sandbox_name, vitoria=False):
    print(f"Iniciando o jogo na Sandboxie {sandbox_name}...")
    numero = re.search(r'\d+', sandbox_name).group()
    titulo_janela = f"[{numero}] AxieInfinity-Origins"
    restaurar_reg_hive(sandbox_name)
    subprocess.Popen([SANDBOXIE_PATH, f"/box:{sandbox_name}", GAME_PATH])
    time.sleep(5)

    if vitoria:
        window = next((w for w in gw.getAllWindows() if titulo_janela in w.title), None)
        if window:
            if not is_window_384x270(window):
                ajustar_janela(window, window.title, lock, ocupacao_grid)

def is_window_valid(window):
    try:
        _ = window.left
        return True
    except gw.PyGetWindowException:
        return False
    
def jogar_origin():
    game_windows = [window for window in gw.getAllWindows() if "AxieInfinity-Origins" in window.title]

    for window in game_windows:
        if is_window_valid(window):
            try:
                window.activate()
            except PyGetWindowException:
                print(f"Erro ao ativar a janela {window.title}. Pulando para a próxima janela.")
                continue

            for img in ['back', 'fechar', 'play', 'cancel', 'cancel-2', 'end-turn', 'draw', 'victory',  'victory-2', 'victory-3', 'defeated', 'defeated-2', 'nextmatch']:
                try:
                    region = (window.left, window.top, window.width, window.height)
                    location = pyautogui.locateCenterOnScreen(
                        f"{IMAGE_PATH}/{img}.png", confidence=0.7, region=region
                    )

                    if not location:    
                        continue

                    if img not in ['end-turn', 'cancel']:
                        pyautogui.click(location)

                    if img == 'play':
                        time.sleep(0.5)
                        play = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/casual.png", confidence=0.7, region=region
                        )
                        if play:
                            time.sleep(0.5)
                            pyautogui.click(play)
                            
                        time.sleep(2)
                        fechar = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/fechar.png", confidence=0.7, region=region
                        )
                        if fechar:
                            time.sleep(0.5)
                            pyautogui.click(fechar)
                            
                            time.sleep(2)
                            back = pyautogui.locateCenterOnScreen(
                                f"{IMAGE_PATH}/back.png", confidence=0.7, region=region
                            )
                            if back:
                                time.sleep(0.5)
                                pyautogui.click(back)               

                    if img == 'cancel':
                        time.sleep(0.5)
                        submit = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/submit.png", confidence=0.7, region=region
                        )
                        if submit:
                            time.sleep(0.5)
                            pyautogui.click(submit)
                            
                        cancel = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/cancel.png", confidence=0.7, region=region
                        )
                        if cancel:
                            time.sleep(0.5)
                            pyautogui.click(cancel)
                            
                    if img == 'cancel-2':
                        time.sleep(0.5)
                            
                        ok = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/ok.png", confidence=0.7, region=region
                        )
                        if ok:
                            time.sleep(0.5)
                            pyautogui.click(ok)   
                            
                        cancel = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/cancel-2.png", confidence=0.7, region=region
                        )
                        if cancel:
                            time.sleep(0.5)
                            pyautogui.click(cancel)             

                    if img == 'end-turn':
                        print("end turn entrou!")
                        window.activate()
                        time.sleep(1)
                        keys = ['1','2','3','4','5','6','enter','e']
                        
                        randomClick = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/random-click.png", confidence=0.7, region=region
                        )
                        randomClick22 = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/random-click-22.png", confidence=0.7, region=region
                        )
                            
                        for key in keys:
                            try:
                                cancel = pyautogui.locateCenterOnScreen(
                                    f"{IMAGE_PATH}/cancel.png", confidence=0.7, region=region
                                )
                                if cancel:
                                    pyautogui.click(cancel)
                            except Exception as e:
                                pass 
                                                    
                            if randomClick:
                                pyautogui.click(randomClick)
                            
                            if randomClick22:
                                pyautogui.click(randomClick22)
                                
                            pyautogui.press(key)
                            time.sleep(0.1)

                    if img in ['victory',  'victory-2', 'victory-3']:
                        print("victory entrou!")
                        processar_vitoria_origin(window, queued_sandboxes, start_game_in_sandbox)
                        
                    if img in ['defeated',  'defeated-2']:
                        pyautogui.click(location)
                        time.sleep(0.5)
                        pyautogui.doubleClick(location)
                        time.sleep(0.5)
                        pyautogui.doubleClick(location)
                            
                    if img in ['draw']:
                        pyautogui.click(location)
                        time.sleep(0.5)
                        pyautogui.doubleClick(location)
                        time.sleep(0.5)
                        pyautogui.doubleClick(location)

                except Exception as e:
                    pass          

def encerrar_bot(event):
    print("Bot encerrado.")
    root.quit()

root = tk.Tk()
root.title("AUTOPLAY - ORIGINS")
root.geometry("384x270")
root.resizable(False, False)

btn_iniciar_bot = tk.Button(root, text="Iniciar Bot", font=("Helvetica", 14), command=iniciar_bot)
btn_iniciar_bot.pack(pady=5)

btn_sair = tk.Button(root, text="Sair do Bot", font=("Helvetica", 14), command=root.quit)
btn_sair.pack(pady=5)

root.mainloop()
