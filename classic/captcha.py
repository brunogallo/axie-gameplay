import os
import cv2
import numpy as np

def get_template(template_path):
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"Template image not found: {template_path}")
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("template_debug.png", template_gray)  # Salva para verificar
    return template_gray

def find_template_in_image(image, template, threshold=0.9):
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(loc[1], loc[0]))  # Coleta das coordenadas
    return points

def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found: {image_path}")
    return image

def search_img(template_path, image_path, confidence=0.9):
    im1 = load_image(image_path)
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)  # Converte para escala de cinza
    template = get_template(template_path)
    points = find_template_in_image(im1_gray, template, confidence)
    if points:
        return True
    return False

def search_axie(category, image_path):
    for f in os.listdir(category):
        if search_img(os.path.join(category, f), image_path):
            return True
    return False

# Caminho da imagem que você já tem salva na raiz
image_path = "screenshot.png"
category = "img"

result = search_axie(category, image_path)
print(result)  # Certifique-se de que este print seja "True" ou "False"
