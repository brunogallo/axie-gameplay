import pygetwindow as gw
import pyautogui
import time
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
from pygetwindow import PyGetWindowException
import sys
import os

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

sandboxie_path = r"C:\Program Files\Sandboxie\Start.exe"
game_path = r"C:\Program Files\Axie Infinity - Origins\AxieInfinity-Origins.exe"
image_path = get_resource_path("img/origin")
resolution = (480, 270)
window_positions = [
    (0, 0), (480, 0), (960, 0), (1440, 0),
    (0, 270), (480, 270), (960, 270), (1440, 270),
    (0, 540), (480, 540)
]
click_coordinates = [
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)],
    [(402, 241), (263, 94)]
]

def fechar_todas_janelas():
    for window in gw.getAllWindows():
        if "AxieInfinity" in window.title:
            window.close()
    print("Todas as janelas do Sandboxie foram fechadas.")

def is_window_valid(window):
    try:
        _ = window.left
        return True
    except PyGetWindowException:
        return False

def start_game_in_sandbox(sandbox_name):
    print(f"Iniciando o jogo na Sandboxie {sandbox_name}...")
    subprocess.Popen([sandboxie_path, f"/box:{sandbox_name}", game_path])

def abrir_janelas():
    num_janelas = simpledialog.askinteger("Input", "Quantas janelas do Sandboxie você quer usar?", minvalue=1, maxvalue=10)
    if num_janelas:
        for i in range(1, num_janelas + 1):
            sandbox_name = str(i)
            start_game_in_sandbox(sandbox_name)
        messagebox.showinfo("Info", f"{num_janelas} janelas abertas no Sandboxie.")

def adjust_windows():
    time.sleep(1)
    game_windows = [window for window in gw.getAllWindows() if "AxieInfinity" in window.title]
    for i in range(len(game_windows)):
        if i < len(window_positions):
            window = game_windows[i]
            window.resizeTo(*resolution)
            window.moveTo(*window_positions[i])
            print(f"Janela do jogo {i + 1} ajustada.")
            time.sleep(1)

def encerrar_bot(event):
    print("Bot encerrado.")
    root.quit()

def perform_clicks(coordinates, window):
    if not is_window_valid(window):
        print(f"Janela {window.title} não é válida.")
        return
    for x, y in coordinates:
        x_abs = window.left + x
        y_abs = window.top + y
        print(f"Clicando em: ({x_abs}, {y_abs}) na janela {window.title}")
        pyautogui.click(x_abs, y_abs)
        time.sleep(0.1)

def executar_cliques_entrada():
    game_windows = [window for window in gw.getAllWindows() if "AxieInfinity" in window.title]
    for i in range(len(game_windows)):
        if i < len(click_coordinates):
            window = game_windows[i]
            perform_clicks(click_coordinates[i], window)
    messagebox.showinfo("Info", "Cliques de entrada realizados em todas as janelas.")

def play_turn(window):
    print(f"Jogando as cartas na janela {window.title}...")
    window.activate()
    time.sleep(1)
    keys = ['1', '2', '3', '4', '5', '6', 'e']
    for key in keys:
        pyautogui.press(key)
        time.sleep(0.1)

def check_end_game(window, queued_sandboxes):
    print(f"Verificando se o jogo acabou na janela {window.title}...")
    end_game_images = ['victory', 'x']
    for img in end_game_images:
        try:
            location = pyautogui.locateCenterOnScreen(f"{image_path}/{img}.png", confidence=0.7)
            if location:
                pyautogui.click(location)
                if img == 'victory':
                    pyautogui.hotkey('alt', 'f4')
                    if queued_sandboxes:
                        next_sandbox = queued_sandboxes.pop(0)
                        start_game_in_sandbox(next_sandbox)
                        print("Pausando para iniciar a nova janela...")
                        time.sleep(4)  # Espera 4 segundos antes de ajustar as janelas
                        adjust_windows()
                        # Adicione uma pausa para garantir que a nova janela seja ajustada corretamente
                        time.sleep(2)
                        # Agora sim, retorne para continuar os cliques
                return
        except pyautogui.ImageNotFoundException:
            continue
        except Exception as e:
            print(f"Erro ao procurar {img} na janela {window.title}: {e}")
            continue

def iniciar_jogo(queued_sandboxes):
    while True:
        game_windows = [window for window in gw.getAllWindows() if "AxieInfinity" in window.title]
        windows_with_nextmatch = set()
        if not game_windows:
            break
        for i, window in enumerate(game_windows[:]):
            try:
                if i in windows_with_nextmatch:
                    continue
                perform_clicks(click_coordinates[i], window)
                play_turn(window)
                check_end_game(window, queued_sandboxes)
            except PyGetWindowException as e:
                print(f"Erro na janela {window.title}: {e}")
                game_windows.remove(window)  # Remove a janela inválida da lista
            except Exception as e:
                print(f"Erro geral na janela {window.title}: {e}")
        time.sleep(0.5)
    messagebox.showinfo("Info", "Jogo concluído em todas as janelas.")

root = tk.Tk()
root.title("Controle de Macro para Axie Infinity")
root.geometry("300x200")
root.bind("<p>", encerrar_bot)

num_total_sandboxes = int(simpledialog.askinteger("Input", "Quantas sandboxes você tem?", minvalue=1))
num_running_sandboxes = int(simpledialog.askinteger("Input", "Quantas sandboxes você quer rodar por vez?", minvalue=1))

total_sandboxes = [str(i + 1) for i in range(num_total_sandboxes)]
queued_sandboxes = total_sandboxes[num_running_sandboxes:]

for sandbox in total_sandboxes[:num_running_sandboxes]:
    start_game_in_sandbox(sandbox)
btn_fechar_janelas = tk.Button(root, text="Fechar Todas Janelas", command=fechar_todas_janelas)
btn_fechar_janelas.pack(pady=5)
btn_abrir_janelas = tk.Button(root, text="Abrir Janelas Sandboxie", command=abrir_janelas)
btn_abrir_janelas.pack(pady=5)
btn_organizar_janelas = tk.Button(root, text="Organizar Janelas", command=adjust_windows)
btn_organizar_janelas.pack(pady=5)
btn_executar_cliques = tk.Button(root, text="Executar Cliques de Entrada", command=executar_cliques_entrada)
btn_executar_cliques.pack(pady=5)
btn_iniciar_jogo = tk.Button(root, text="Iniciar Jogo", command=lambda: iniciar_jogo(queued_sandboxes))
btn_iniciar_jogo.pack(pady=5)
root.mainloop()
