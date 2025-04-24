import shutil
import os
import re

regHive = r"C:\Sandbox"

def restaurar_reg_hive(sandbox_name):
    numero = re.search(r'\d+', sandbox_name).group()
    pasta_sandbox = None

    for pasta in os.listdir(regHive):
        caminho_pasta = os.path.join(regHive, pasta)
        if os.path.isdir(caminho_pasta):
            pasta_sandbox = os.path.join(caminho_pasta, numero)
            break

    if pasta_sandbox and os.path.isdir(pasta_sandbox):
        reg_hive_path = os.path.join(pasta_sandbox, 'RegHive')
        reg_hive_bkp_path = os.path.join(pasta_sandbox, 'RegHive-bkp')

        if os.path.exists(reg_hive_path):
            os.remove(reg_hive_path)

        if os.path.exists(reg_hive_bkp_path):
            shutil.copy(reg_hive_bkp_path, reg_hive_path)
        else:
            print(f"Backup RegHive-bkp não encontrado em {pasta_sandbox}")
    else:
        print(f"Pasta {numero} não encontrada em {regHive}")

def reset_bot():
    regHive = r"C:\Sandbox"

    try:
        subdirs = [d for d in os.listdir(regHive) if os.path.isdir(os.path.join(regHive, d))]
        if not subdirs:
            print("Nenhuma subpasta encontrada em C:\\Sandbox")
            return

        for subdir in subdirs:
            caminho_subdir = os.path.join(regHive, subdir)
            for pasta in os.listdir(caminho_subdir):
                caminho_pasta = os.path.join(caminho_subdir, pasta)
                if os.path.isdir(caminho_pasta):
                    reg_hive_path = os.path.join(caminho_pasta, 'RegHive')
                    backup_path = os.path.join(caminho_pasta, 'RegHive-bkp')
                    if os.path.exists(reg_hive_path):
                        shutil.copy2(reg_hive_path, backup_path)
                        print(f"Backup criado: {backup_path}")
                    else:
                        print(f"Arquivo RegHive não encontrado em: {caminho_pasta}")

    except Exception as e:
        print(f"Erro ao resetar bot: {e}")