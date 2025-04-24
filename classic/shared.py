import threading

lock = threading.Lock()

resolution = (384, 270)
window_positions = [(x, y) for y in range(0, 1080, 270) for x in range(0, 1920, 384)]
ocupacao_grid = [None] * len(window_positions)