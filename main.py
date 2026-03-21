import cv2
import numpy as np
import mss
import time

class Environment:
    def __init__(self):
        self.HEX_L = "#b76635"
        self.HEX_L_INV = "#503fa5"
        self.HEX_S = "#82b231"
        self.HEX_S_INV = "#b9383f"
        self.HEX_P = "#31b282"
        self.HEX_C = "#b49a33"
        self.HEX_T = "#a63f9c"

        self.HEX_A_L = "#e47129"
        self.HEX_A_L_INV = "#553ccf"
        self.HEX_A_S = "#a0e52b"
        self.HEX_A_S_INV = "#e42d37"
        self.HEX_A_P = "#2de6a1"
        self.HEX_A_C = "#e3bf29"
        self.HEX_A_T = "#ce3bbf"

        self.color_map = {
            self.hex_to_rgb(self.HEX_L): "L",
            self.hex_to_rgb(self.HEX_L_INV): "LI",
            self.hex_to_rgb(self.HEX_S): "S",
            self.hex_to_rgb(self.HEX_S_INV): "SI",
            self.hex_to_rgb(self.HEX_P): "P",
            self.hex_to_rgb(self.HEX_C): "C",
            self.hex_to_rgb(self.HEX_T): "T"
        }

        self.color_map_above = {
            self.hex_to_rgb(self.HEX_A_L): "L",
            self.hex_to_rgb(self.HEX_A_L_INV): "LI",
            self.hex_to_rgb(self.HEX_A_S): "S",
            self.hex_to_rgb(self.HEX_A_S_INV): "SI",
            self.hex_to_rgb(self.HEX_A_P): "P",
            self.hex_to_rgb(self.HEX_A_C): "C",
            self.hex_to_rgb(self.HEX_A_T): "T"
        }

        self.BOARD = self.seleccionar_area("Selecciona el área del tablero", self.screenshot())
        self.NEXT = self.seleccionar_area("Selecciona el área de next", self.screenshot())
        self.HOLD = self.seleccionar_area("Selecciona el área de hold", self.screenshot())
        self.ABOVE = self.seleccionar_area("Selecciona el área de above", self.screenshot())

    def seleccionar_area(self, nombre, imagen):
        time.sleep(2)  # Pequeña pausa para que el usuario pueda prepararse
        r = cv2.selectROI(nombre, imagen, False, False)
        cv2.destroyWindow(nombre)

        x,y,w,h = r

        region = {
            "top": int(y),
            "left": int(x),
            "width": int(w),
            "height": int(h)
        }

        return region

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def capturar_region(self, region):
        with mss.mss() as sct:
            img = np.array(sct.grab(region))
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def screenshot():
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def analizar_grid(self, img, filas, columnas, board=False, color_map_param=None):
        if color_map_param is None:
            color_map_param = self.color_map

        h, w, _ = img.shape

        cell_h = h // filas
        cell_w = w // columnas

        matriz = []

        for f in range(filas):
            fila = []
            for c in range(columnas):
                y1 = f * cell_h
                y2 = (f+1) * cell_h
                x1 = c * cell_w
                x2 = (c+1) * cell_w

                celda = img[y1:y2, x1:x2]

                if not board:
                    # detectar si existe algún pixel con color de pieza
                    found_color = None
                    for pixel in celda.reshape(-1, 3):
                        b, g, r = pixel
                        rgb = (int(r), int(g), int(b))
                        if rgb in color_map_param:
                            found_color = color_map_param[rgb]
                            break

                    if found_color:
                        fila.append(found_color)
                    else:
                        fila.append(".")
                else:
                    # color promedio
                    b,g,r = np.mean(celda.reshape(-1,3), axis=0)
                    brillo = (r+g+b)/3
                    if brillo < 40:
                        fila.append(".")
                    else:
                        fila.append("#")

            matriz.append(fila)

        return matriz

    def percept(self):
        board_img = self.capturar_region(self.BOARD)
        next_img = self.capturar_region(self.NEXT)
        hold_img = self.capturar_region(self.HOLD)
        above_img = self.capturar_region(self.ABOVE)

        board_grid = self.analizar_grid(board_img, 20, 10, True)
        above_grid = self.analizar_grid(above_img, 1, 1, color_map_param=self.color_map_above)
        next_grid = self.analizar_grid(next_img, 5, 1)
        hold_grid = self.analizar_grid(hold_img, 1, 1)

        return {
            'board': board_grid,
            'above': above_grid,
            'next': next_grid,
            'hold': hold_grid
        }

# Main code
env = Environment()

print("Iniciando captura...")

state = env.percept()