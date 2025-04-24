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
from classic.janela import fechar_todas_janelas
from classic.janela import esperar_carregamento_janela
from classic.janela import ajustar_janela
from classic.janela import esperar_todas_janelas
from classic.regHive import restaurar_reg_hive
from classic.regHive import reset_bot
from classic.vitoria import obter_sandboxes_com_vitoria
from classic.vitoria import processar_vitoria
from classic.vitoria import processar_quest
from classic.janela import is_window_384x270
from classic.shared import lock, ocupacao_grid

SANDBOXIE_PATH = r"C:\Program Files\Sandboxie\Start.exe"
GAME_PATH = r"C:\Program Files\Axie Classic\axie_game.exe"
IMAGE_PATH = r"img/classic"
REGHIVE_PATH = r"C:\Sandbox"
FILA_PATH = 'contas.json'

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

    if esperar_todas_janelas(num_running_sandboxes):
        time.sleep(2)
        while True:
            print("dsada")
            jogar_classic()
            
def claim_quest():
    global queued_sandboxes
    global num_total_sandboxes
        
    num_total_sandboxes = int(simpledialog.askinteger("Input", "Quantas sandboxes você tem?", minvalue=1))
    num_running_sandboxes = int(simpledialog.askinteger("Input", "Quantas sandboxes você quer rodar por vez?", minvalue=1))

    total_sandboxes = [str(i + 1) for i in range(num_total_sandboxes)]
    queued_sandboxes = total_sandboxes[num_running_sandboxes:]

    for sandbox in total_sandboxes[:num_running_sandboxes]:
        t = threading.Thread(target=start_game_in_sandbox, args=(sandbox,))
        threads.append(t)
        t.start()

    if esperar_todas_janelas(num_running_sandboxes):
        time.sleep(2)
        while True:
            quest()
            
def start_game_in_sandbox(sandbox_name, vitoria=False):
    print(f"Iniciando o jogo na Sandboxie {sandbox_name}...")
    numero = re.search(r'\d+', sandbox_name).group()
    titulo_janela = f"[{numero}] Axie Infinity"
    restaurar_reg_hive(sandbox_name)
    subprocess.Popen([SANDBOXIE_PATH, f"/box:{sandbox_name}", GAME_PATH])
    time.sleep(5)

    if vitoria:
        window = next((w for w in gw.getAllWindows() if titulo_janela in w.title), None)
        if window:
            if not is_window_384x270(window):
                print(f"{window.title}. AJUSTANDUUU...")
                ajustar_janela(window, window.title, lock, ocupacao_grid)

def is_window_valid(window):
    try:
        _ = window.left
        return True
    except gw.PyGetWindowException:
        return False
    
def jogar_classic():
    game_windows = [window for window in gw.getAllWindows() if "Axie Infinity" in window.title]

    for window in game_windows:
        if is_window_valid(window):
            try:
                window.activate()
            except PyGetWindowException:
                print(f"Erro ao ativar a janela {window.title}. Pulando para a próxima janela.")
                continue

            for img in ['fechar', 'fechar-2', 'ok', 'play', 'prox-turno', 'vitoria', 'derrota', 'empate', 'empate-2']:
                try:
                    region = (window.left, window.top, window.width, window.height)
                    location = pyautogui.locateCenterOnScreen(
                        f"{IMAGE_PATH}/{img}.png", confidence=0.7, region=region
                    )

                    if not location:    
                        continue

                    if img not in ['prox-turno']:
                        print(f"{img} encontrado na posição {location} na janela {window.title}.")
                        pyautogui.click(location)

                    if img == 'play':
                        play = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/arena.png", confidence=0.7, region=region
                        )
                        if play:
                            time.sleep(0.5)
                            pyautogui.click(play)

                    if img == 'prox-turno':
                        window.activate()
                        prox_turno = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/prox-turno.png", confidence=0.7, region=region
                        )
                        escala_x = 384 / 1920
                        escala_y = 270 / 1080

                        if prox_turno:
                            for x_virtual in range(1516, 324, -35):
                                x_ajustado = int(x_virtual * escala_x)
                                y_ajustado = int(990 * escala_y)
                                pyautogui.click(window.left + x_ajustado, window.top + y_ajustado)

                            time.sleep(0.2)
                            pyautogui.click(prox_turno)

                    if img == 'vitoria':
                        pyautogui.click(location)
                        time.sleep(0.5)
                        vitoria = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/vitoria-2.png", confidence=0.5, region=region
                        )
                        if vitoria:
                            pyautogui.doubleClick(vitoria)
                            time.sleep(1)
                            pyautogui.doubleClick(vitoria)
                            processar_vitoria(window, queued_sandboxes, start_game_in_sandbox)
                            
                    if img == 'derrota':
                        pyautogui.click(location)
                        time.sleep(0.5)
                        derrota = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/derrota-2.png", confidence=0.7, region=region
                        )
                        if derrota:
                            pyautogui.click(derrota)
                            
                    if img in ['empate', 'empate-2']:
                        pyautogui.click(location)
                        time.sleep(0.5)
                        empate = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/empate-3.png", confidence=0.7, region=region
                        )
                        if empate:
                            pyautogui.doubleClick(empate)
                            time.sleep(1)
                            pyautogui.doubleClick(empate)

                except Exception as e:
                    pass          

def quest():
    game_windows = [window for window in gw.getAllWindows() if "Axie Infinity" in window.title]

    for window in game_windows:
        window.activate()
        region = (window.left, window.top, window.width, window.height)

        for img in ['rodar-roleta','bau-1','bau-2','quest','quest-2','fechar', 'fechar-2', 'close-bau', 'ok']:
            try:
                location = pyautogui.locateCenterOnScreen(
                    f"{IMAGE_PATH}/{img}.png", confidence=0.7, region=region
                )        
                pyautogui.click(location)
                time.sleep(1)
                                            
                if img in ['bau-1', 'bau-2']:
                    time.sleep(0.5)
                    open_bau = pyautogui.locateCenterOnScreen(
                        f"{IMAGE_PATH}/open-bau.png", confidence=0.7, region=region
                    )
                    if open_bau:
                        time.sleep(1.5)
                        pyautogui.click(open_bau)
                        close_bau = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/close-bau.png", confidence=0.7, region=region
                        )
                        if close_bau:
                            pyautogui.click(close_bau)

                if img in ['rodar-roleta']:
                    open_bau = pyautogui.locateCenterOnScreen(
                        f"{IMAGE_PATH}/open-bau.png", confidence=0.7, region=region
                    )
                    if open_bau:
                        time.sleep(3.5)
                        pyautogui.click(open_bau)
                        close_bau = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/fechar.png", confidence=0.7, region=region
                        )
                        if close_bau:
                            pyautogui.click(close_bau)

                if img == 'quest':
                    pyautogui.click(location)
                    time.sleep(1)
                
                    time.sleep(1)
                    escala_x = 384 / 1920
                    escala_y = 270 / 1080

                    coordenadas = [
                        (1125, 165), (1120, 166),
                        (82, 145)
                    ]

                    coordenadas_ajustadas = [(int(x * escala_x), int(y * escala_y)) for x, y in coordenadas]
                    for x, y in coordenadas_ajustadas:
                        pyautogui.click(window.left + x, window.top + y)
                        time.sleep(0.5)
                        
                    processar_quest(window, queued_sandboxes, start_game_in_sandbox)

                if img == 'quest-2':
                    time.sleep(1)
                    escala_x = 384 / 1920
                    escala_y = 270 / 1080

                    coordenadas = [
                        (1125, 165), (1120, 166),
                        (82, 145)
                    ]

                    coordenadas_ajustadas = [(int(x * escala_x), int(y * escala_y)) for x, y in coordenadas]
                    for x, y in coordenadas_ajustadas:
                        pyautogui.click(window.left + x, window.top + y)
                        time.sleep(0.5)
                        
                    processar_quest(window, queued_sandboxes, start_game_in_sandbox)
                    
            except Exception as e:
                pass          
            
def encerrar_bot(event):
    print("Bot encerrado.")
    root.quit()

root = tk.Tk()
root.title("AUTOPLAY - CLASSIC")
root.geometry("384x270")
root.resizable(False, False)

btn_iniciar_bot = tk.Button(root, text="Iniciar Bot", font=("Helvetica", 14), command=iniciar_bot)
btn_iniciar_bot.pack(pady=5)

btn_iniciar_bot = tk.Button(root, text="Claim Quest", font=("Helvetica", 14), command=claim_quest)
btn_iniciar_bot.pack(pady=5)

btn_reset_bot = tk.Button(root, text="Reset Bot", font=("Helvetica", 14), command=reset_bot)
btn_reset_bot.pack(pady=5)

btn_sair = tk.Button(root, text="Sair do Bot", font=("Helvetica", 14), command=root.quit)
btn_sair.pack(pady=5)

btn_fechar_todas = tk.Button(root, text="Fechar Todas", font=("Helvetica", 14), command=fechar_todas_janelas)
btn_fechar_todas.pack(pady=5)

root.mainloop()
