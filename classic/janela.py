import pygetwindow as gw
import pyautogui
import time
import threading
import re
from pygetwindow import PyGetWindowException
from classic.grade import liberar_posicao_por_titulo
from classic.grade import encontrar_primeira_posicao_livre
from classic.grade import marcar_posicao_ocupada
from classic.shared import lock, ocupacao_grid, resolution, window_positions

def is_window_valid(window):
    try:
        _ = window.left
        return True
    except PyGetWindowException:
        return False

def sair_do_fullscreen(window):
    window.restore()
    window.activate()
    time.sleep(0.5)
    pyautogui.hotkey('alt', 'enter')
    time.sleep(1)
    
def fechar_todas_janelas():
    for window in gw.getAllWindows():
        if re.search(r"\[(\d+)\] Axie Infinity", window.title):
            window.close()

def esperar_sair_do_fullscreen(window, timeout=10):
    tempo_inicial = time.time()
    while is_fullscreen(window):
        if time.time() - tempo_inicial > timeout:
            window.activate()
            sair_do_fullscreen(window)
            return False
        time.sleep(0.5)
    return True

def esperar_carregamento_janela(window, tempo_maximo=20):
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < tempo_maximo:
        try:
            if window.isActive:
                print(f"Janela '{window.title}' parece estar pronta.")
                return True
        except:
            pass
        time.sleep(1)
    return False
 
def is_fullscreen(window):
    screen_width, screen_height = pyautogui.size()
    win_left, win_top, win_width, win_height = window.left, window.top, window.width, window.height

    tolerance = 10

    is_fullscreen = (
        abs(win_width - screen_width) <= tolerance and
        abs(win_height - screen_height) <= tolerance and
        win_left <= 0 and
        win_top <= 0
    )

    return is_fullscreen

def fechar_janela_e_liberar(titulo):
    window = next((w for w in gw.getAllWindows() if titulo in w.title), None)
    if window:
        window.close()
        liberar_posicao_por_titulo(titulo, ocupacao_grid)

def ajustar_janela(window, titulo, lock, ocupacao_grid):
    with lock:
        posicao = encontrar_primeira_posicao_livre(ocupacao_grid)
        
        # If there is a free position, adjust the window
        if posicao is not None:
            x, y = window_positions[posicao]
            window.resizeTo(*resolution)
            window.moveTo(x, y)
            marcar_posicao_ocupada(posicao, titulo, ocupacao_grid)
        else:
            print("No free positions available.")

def is_window_384x270(window):
    target_width, target_height = 384, 270
    win_left, win_top, win_width, win_height = window.left, window.top, window.width, window.height

    tolerance = 10

    matches_resolution = (
        abs(win_width - target_width) <= tolerance and
        abs(win_height - target_height) <= tolerance
    )

    return matches_resolution
 
def esperar_todas_janelas(num_esperado, timeout=60, classic=True):
    tempo_inicial = time.time()
    print("Iniciando função. Timeout:", timeout, "Modo Classic:", classic)

    while time.time() - tempo_inicial < timeout:
        print("Looping while ativo. Tempo decorrido:", round(time.time() - tempo_inicial, 2))
        
        if classic:
            print("Buscando janelas (classic mode)...")
            janelas_abertas = [w for w in gw.getAllWindows() if re.search(r"\[\d+\] Axie Infinity", w.title)]
        else:
            print("Buscando janelas (non-classic mode)...")
            janelas_abertas = [w for w in gw.getAllWindows() if "AxieInfinity" in w.title]

        print("Janelas encontradas:", [w.title for w in janelas_abertas])

        if len(janelas_abertas) >= num_esperado:
            print(f"Encontradas {len(janelas_abertas)} janelas. Processando...")
            for janela in janelas_abertas:
                print(f"Verificando janela: {janela.title}")
                if not is_window_384x270(janela):
                    print(f"Ajustando tamanho da janela: {janela.title}")
                    ajustar_janela(janela, janela.title, lock, ocupacao_grid)
            return True

        print("Ainda não encontrou janelas suficientes. Aguardando 5 segundos...")
        time.sleep(5)

    print("Timeout atingido. Saindo da função.")
    return False