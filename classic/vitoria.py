import os
import re
import json
from datetime import datetime
from classic.janela import fechar_janela_e_liberar
import threading
FILA_PATH = 'contas.json'
FILA_PATH_ORIGIN = 'contas-origin.json'
FILA_PATH_PREMIUM = 'contas-premium.json'
fila_lock = threading.Lock()

def obter_sandboxes_com_vitoria(type):
    hoje = datetime.now().strftime("%Y-%m-%d")
    if type == "premium":
        caminho_arquivo_vitorias = f"{hoje}_premium.txt"
    else:
        caminho_arquivo_vitorias = f"{hoje}.txt"
    sandboxes_vencedoras = []

    if os.path.exists(caminho_arquivo_vitorias):
        with open(caminho_arquivo_vitorias, 'r') as arquivo:
            vitorias = arquivo.readlines()
            titulos_ocorrencias = {}

            for vitoria in vitorias:
                vitoria = vitoria.strip()
                match = re.search(r"\[\#\] \[(\d+)\] Axie Infinity", vitoria)
                if match:
                    numero_sandbox = match.group(1)
                    if numero_sandbox in titulos_ocorrencias:
                        titulos_ocorrencias[numero_sandbox] += 1
                    else:
                        titulos_ocorrencias[numero_sandbox] = 1

            if type == "premium":
                sandboxes_vencedoras = [
                    numero for numero, ocorrencias in titulos_ocorrencias.items() if ocorrencias >= 2
                ]
            else:
                sandboxes_vencedoras = list(titulos_ocorrencias.keys())

    return sandboxes_vencedoras

def salvar_vencedor(sandbox):
    with fila_lock:
        try:
            with open(FILA_PATH, 'r') as f:
                vencedores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            vencedores = []

        if sandbox not in vencedores:
            vencedores.append(sandbox)
            with open(FILA_PATH, 'w') as f:
                json.dump(vencedores, f, indent=4)
            print(f"[{sandbox}] Salva como vencedora.")
        else:
            print(f"[{sandbox}] Já estava salva como vencedora.")

def salvar_vencedor_premium(sandbox):
    with fila_lock:
        try:
            with open(FILA_PATH_PREMIUM, 'r') as f:
                vencedores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            vencedores = []

        if sandbox not in vencedores:
            vencedores.append(sandbox)
            with open(FILA_PATH_PREMIUM, 'w') as f:
                json.dump(vencedores, f, indent=4)
            print(f"[{sandbox}] Salva como vencedora.")
        else:
            print(f"[{sandbox}] Já estava salva como vencedora.")
            
def salvar_vencedor_origin(sandbox):
    with fila_lock:
        try:
            with open(FILA_PATH_ORIGIN, 'r') as f:
                vencedores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            vencedores = []

        if sandbox not in vencedores:
            vencedores.append(sandbox)
            with open(FILA_PATH_ORIGIN, 'w') as f:
                json.dump(vencedores, f, indent=4)
            print(f"[{sandbox}] Salva como vencedora.")
        else:
            print(f"[{sandbox}] Já estava salva como vencedora.")
                        
def processar_vitoria(window, queued_sandboxes, start_game_in_sandbox):
    global fila_lock
    
    titulo_janela = window.title
    match = re.search(r"\[(#|x)\] \[(\d+)\] Axie Infinity \[(#|x)\]", titulo_janela)
    
    if match:
        id = match.group(2)
        salvar_vencedor(id)
        fechar_janela_e_liberar(titulo_janela)
    else:
        print("No match found")

    with fila_lock:
        if queued_sandboxes:
            proxima_sandbox = queued_sandboxes.pop(0)
            print(f"Abrindo nova sandbox: {proxima_sandbox}")
            threading.Thread(target=start_game_in_sandbox, args=(proxima_sandbox,True,)).start()
        else:
            print("Fila vazia! Nenhuma nova sandbox para abrir.")

    #exibir_ocupacao_grid()

def processar_vitoria_origin(window, queued_sandboxes, start_game_in_sandbox):
    global fila_lock
    
    titulo_janela = window.title
    print(titulo_janela)
    match = re.search(r"\[(#|x)\] \[(\d+)\] AxieInfinity-Origins \[(#|x)\]", titulo_janela)
    
    if match:
        id = match.group(2)
        salvar_vencedor_origin(id)
        fechar_janela_e_liberar(titulo_janela)
    else:
        print("No match found")

    with fila_lock:
        if queued_sandboxes:
            proxima_sandbox = queued_sandboxes.pop(0)
            print(f"Abrindo nova sandbox: {proxima_sandbox}")
            threading.Thread(target=start_game_in_sandbox, args=(proxima_sandbox,True,)).start()
        else:
            print("Fila vazia! Nenhuma nova sandbox para abrir.")
            
            
def processar_vitoria_premium(window, queued_sandboxes, start_game_in_sandbox):
    global fila_lock
    
    titulo_janela = window.title
    match = re.search(r"\[(#|x)\] \[(\d+)\] Axie Infinity \[(#|x)\]", titulo_janela)
    
    if match:
        id = match.group(2)
        salvar_vencedor_premium(id)
        fechar_janela_e_liberar(titulo_janela)
    else:
        print("No match found")

    with fila_lock:
        if queued_sandboxes:
            proxima_sandbox = queued_sandboxes.pop(0)
            print(f"Abrindo nova sandbox: {proxima_sandbox}")
            threading.Thread(target=start_game_in_sandbox, args=(proxima_sandbox,True,)).start()
        else:
            print("Fila vazia! Nenhuma nova sandbox para abrir.")           
            
def processar_quest(window, queued_sandboxes, start_game_in_sandbox):
    global fila_lock
    
    titulo_janela = window.title
    match = re.search(r"\[(#|x)\] \[(\d+)\] Axie Infinity \[(#|x)\]", titulo_janela)
    
    if match:
        id = match.group(2)
        fechar_janela_e_liberar(titulo_janela)
    else:
        print("No match found")

    with fila_lock:
        if queued_sandboxes:
            proxima_sandbox = queued_sandboxes.pop(0)
            print(f"Abrindo nova sandbox: {proxima_sandbox}")
            threading.Thread(target=start_game_in_sandbox, args=(proxima_sandbox,True,)).start()
        else:
            print("Fila vazia! Nenhuma nova sandbox para abrir.")