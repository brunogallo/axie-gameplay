from classic.shared import ocupacao_grid

def liberar_posicao_por_titulo(titulo, ocupacao_grid):
    for i, ocupacao in enumerate(ocupacao_grid):
        if ocupacao in titulo:
            ocupacao_grid[i] = None
            return i
    return None


def encontrar_primeira_posicao_livre(ocupacao_grid):
    for i, ocupacao in enumerate(ocupacao_grid):
        if ocupacao is None:
            return i
    return None

def marcar_posicao_ocupada(posicao, titulo, ocupacao_grid):
    ocupacao_grid[posicao] = titulo

def exibir_ocupacao_grid(ocupacao_grid):
    print("Status do Grid:")
    for i, ocupacao in enumerate(ocupacao_grid):
        status = ocupacao if ocupacao else "LIVRE"
        print(f"Posição {i}: {status}")
        
        
        
        
        
        


