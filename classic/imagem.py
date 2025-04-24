import pyautogui
image_path = r"img/classic"

def procurar_imagem(imagens):
    for img in imagens:
        image = f"{image_path}/{img}.png"
        try:
            location = pyautogui.locateCenterOnScreen(image, confidence=0.7)
            if location:
                return location
        except Exception as e:
            print(f"Erro ao tentar localizar {img}.png: {e}")
    return None