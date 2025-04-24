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
from classic.vitoria import processar_vitoria_premium
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
    total_sandboxes = set()  # 🔹 Inicializa corretamente como um conjunto

    if entrada:
        partes = entrada.split(",")
        for parte in partes:
            parte = parte.strip()
            if "-" in parte:  # Intervalo (ex: '15-30')
                match = re.match(r'(\d+)-(\d+)', parte)
                if match:
                    start, end = int(match.group(1)), int(match.group(2))
                    total_sandboxes.update(str(i) for i in range(start, end + 1))
                else:
                    print(f"Entrada inválida: {parte}. Exemplo válido: '15', '15-30' ou '1,6,9,16,77,22'.")
                    exit()
            else:  # Número único (ex: '10')
                if parte.isdigit():
                    total_sandboxes.add(parte)
                else:
                    print(f"Entrada inválida: {parte}.")
                    exit()

    # Removemos as vencedoras da lista
    total_sandboxes = sorted(total_sandboxes - set(sandboxes_vencedoras), key=int)
    queued_sandboxes = total_sandboxes[num_running_sandboxes:]

    # Abrir as primeiras sandboxes
    for sandbox in total_sandboxes[:num_running_sandboxes]:
        t = threading.Thread(target=start_game_in_sandbox, args=(sandbox,))
        threads.append(t)
        t.start()

    if esperar_todas_janelas(num_running_sandboxes):
        time.sleep(2)
        while True:
            jogar_classic()
            
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
                        print("cliquei coliseum")
                        play = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/coliseum.png", confidence=0.7, region=region
                        )
                        if play:
                            time.sleep(1)
                            pyautogui.click(play)
                            time.sleep(0.5)
                            
                            for _ in range(10):
                                for img in ['bau-coliseum', 'enter-coliseum', 'edit-team-coliseum', 'ok']:
                                    try:
                                        coliseum_location = pyautogui.locateCenterOnScreen(
                                            f"{IMAGE_PATH}/{img}.png", confidence=0.7, region=region
                                        )

                                        if not coliseum_location:    
                                            continue
                                        
                                        if img == 'enter-coliseum':
                                            time.sleep(0.5)
                                            pyautogui.click(coliseum_location)
                                            time.sleep(0.5)
                                            
                                        if img == 'edit-team-coliseum':
                                            time.sleep(0.5)
                                            pyautogui.click(coliseum_location)

                                            time.sleep(1)
                                            escala_x = 384 / 1920
                                            escala_y = 270 / 1080

                                            coordenadas = [
                                                (512, 830), (512, 600),
                                                (812, 830), (812, 600),
                                                (1115, 830), (1115, 600),
                                                (1400, 830), (1400, 600)
                                            ]

                                            coordenadas_ajustadas = [(int(x * escala_x), int(y * escala_y)) for x, y in coordenadas]
                                            for x, y in coordenadas_ajustadas:
                                                pyautogui.click(window.left + x, window.top + y)
                                                time.sleep(0.5)

                                            save = pyautogui.locateCenterOnScreen(
                                                f"{IMAGE_PATH}/save.png", confidence=0.7, region=region
                                            )
                                            if save:
                                                time.sleep(0.5)
                                                pyautogui.click(save)
                                                time.sleep(1)

                                                enter = pyautogui.locateCenterOnScreen(
                                                    f"{IMAGE_PATH}/fight-coliseum.png", confidence=0.7, region=region
                                                )
                                                if enter:
                                                    time.sleep(0.5)
                                                    pyautogui.click(enter)
                                        
                                        if img == 'bau-coliseum':
                                            time.sleep(0.5)
                                            pyautogui.click(coliseum_location)
                                            
                                            time.sleep(1) 
                                            close_bau = pyautogui.locateCenterOnScreen(
                                                f"{IMAGE_PATH}/close-bau.png", confidence=0.7, region=region
                                            )
                                            if close_bau:
                                                pyautogui.click(close_bau)
                                        
                                        if img == 'ok':
                                            time.sleep(0.5)
                                            pyautogui.click(coliseum_location)
                                        
                                    except Exception as e:
                                        pass  
                            
                            time.sleep(1)

                    if img == 'prox-turno':
                        window.activate()
                        time.sleep(0.5)
                        prox_turno = pyautogui.locateCenterOnScreen(
                            f"{IMAGE_PATH}/prox-turno.png", confidence=0.7, region=region
                        )
                        escala_x = 384 / 1920
                        escala_y = 270 / 1080
                        time.sleep(0.5)

                        if prox_turno:
                            for x_virtual in range(324, 1516, +40):
                                x_ajustado = int(x_virtual * escala_x)
                                y_ajustado = int(990 * escala_y)
                                pyautogui.click(window.left + x_ajustado, window.top + y_ajustado)

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
                            processar_vitoria_premium(window, queued_sandboxes, start_game_in_sandbox)
                            
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
          
def encerrar_bot(event):
    print("Bot encerrado.")
    root.quit()

root = tk.Tk()
root.title("AUTOPLAY - CLASSIC")
root.geometry("384x270")
root.resizable(False, False)

btn_iniciar_bot = tk.Button(root, text="Iniciar Bot", font=("Helvetica", 14), command=iniciar_bot)
btn_iniciar_bot.pack(pady=5)

btn_sair = tk.Button(root, text="Sair do Bot", font=("Helvetica", 14), command=root.quit)
btn_sair.pack(pady=5)

root.mainloop()
