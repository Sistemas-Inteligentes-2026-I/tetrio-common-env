import cv2
import numpy as np
import mss
import time
import pyautogui

BOARD_W = 10
BOARD_H = 20


# ============================================================
# PIEZAS
# ============================================================

_RAW_PIECES = {
    "C":[[[1,1],[1,1]]],

    "P":[
        [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
        [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]],
        [[0,0,0,0],[0,0,0,0],[1,1,1,1],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]]
    ],

    "T":[
        [[0,1,0],[1,1,1],[0,0,0]],
        [[0,1,0],[0,1,1],[0,1,0]],
        [[0,0,0],[1,1,1],[0,1,0]],
        [[0,1,0],[1,1,0],[0,1,0]]
    ],

    "L":[
        [[0,0,1],[1,1,1],[0,0,0]],
        [[0,1,0],[0,1,0],[0,1,1]],
        [[0,0,0],[1,1,1],[1,0,0]],
        [[1,1,0],[0,1,0],[0,1,0]]
    ],

    "LI":[
        [[1,0,0],[1,1,1],[0,0,0]],
        [[0,1,1],[0,1,0],[0,1,0]],
        [[0,0,0],[1,1,1],[0,0,1]],
        [[0,1,0],[0,1,0],[1,1,0]]
    ],

    "S":[
        [[0,1,1],[1,1,0],[0,0,0]],
        [[0,1,0],[0,1,1],[0,0,1]],
        [[0,0,0],[0,1,1],[1,1,0]],
        [[1,0,0],[1,1,0],[0,1,0]]
    ],

    "SI":[
        [[1,1,0],[0,1,1],[0,0,0]],
        [[0,0,1],[0,1,1],[0,1,0]],
        [[0,0,0],[1,1,0],[0,1,1]],
        [[0,1,0],[1,1,0],[1,0,0]]
    ]
}

PIECES = {k:[np.array(r,dtype=np.int8) for r in v] for k,v in _RAW_PIECES.items()}

BOARD_W = 10
BOARD_H = 20

class Agent:

    def __init__(self):

        self.board = np.zeros((BOARD_H, BOARD_W), dtype=np.int8)
        self.last_queue = None

        self.weights = {
            "lines": 5.0,
            "holes": -50.0,
            "height": -0.35,
            "bumpiness": -0.18,
            "well": 3.0
        }

        # precalcular bounds
        self.bounds = {}

        for p, rots in PIECES.items():
            self.bounds[p] = []
            for r in rots:
                ys, xs = np.where(r == 1)
                self.bounds[p].append((xs.min(), xs.max(), ys.min(), ys.max()))

    # ---------------------------------------------------------

    def column_heights(self, board):

        heights = np.zeros(BOARD_W)

        for x in range(BOARD_W):

            col = board[:, x]
            filled = np.where(col)[0]

            if filled.size:
                heights[x] = BOARD_H - filled[0]

        return heights

    # ---------------------------------------------------------

    def holes(self, board):

        holes = 0

        for x in range(BOARD_W):

            col = board[:, x]
            filled = np.where(col)[0]

            if filled.size:
                top = filled[0]
                holes += np.sum(col[top:] == 0)

        return holes

    # ---------------------------------------------------------

    def bumpiness(self, heights):

        return np.sum(np.abs(np.diff(heights)))

    # ---------------------------------------------------------

    def clear_lines(self, board):

        full = np.all(board, axis=1)
        lines = np.sum(full)

        if lines:
            board = board[~full]
            board = np.vstack((np.zeros((lines, BOARD_W)), board))

        return board, lines

    # ---------------------------------------------------------

    def collision(self, board, piece, bounds, x, y):

        min_x, max_x, min_y, max_y = bounds

        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):

                if piece[py][px]:

                    bx = x + px - min_x
                    by = y + py - min_y

                    if bx < 0 or bx >= BOARD_W:
                        return True

                    if by >= BOARD_H:
                        return True

                    if by >= 0 and board[by][bx]:
                        return True

        return False

    # ---------------------------------------------------------

    def drop_piece(self, board, piece, bounds, x):

        min_x, max_x, min_y, max_y = bounds
        height = max_y - min_y + 1

        for y in range(BOARD_H):

            if self.collision(board, piece, bounds, x, y):
                y -= 1
                break
        else:
            y = BOARD_H - height

        if y < 0:
            return None

        new_board = board.copy()

        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):

                if piece[py][px]:

                    bx = x + px - min_x
                    by = y + py - min_y

                    new_board[by][bx] = 1

        new_board, lines = self.clear_lines(new_board)

        return new_board, lines

    # ---------------------------------------------------------

    def evaluate(self, board, lines):

        heights = self.column_heights(board)

        holes = self.holes(board)

        bump = self.bumpiness(heights)

        height_sum = np.sum(heights)

        well_penalty = heights[-1]

        return (
            self.weights["lines"] * lines +
            self.weights["holes"] * holes +
            self.weights["height"] * height_sum +
            self.weights["bumpiness"] * bump -
            self.weights["well"] * well_penalty
        )

    # ---------------------------------------------------------

    def possible_moves(self, board, piece):

        moves = []

        rots = PIECES[piece]

        for r in range(len(rots)):

            rot = rots[r]
            bounds = self.bounds[piece][r]

            min_x, max_x, _, _ = bounds
            w = max_x - min_x + 1

            for x in range(BOARD_W - w + 1):

                result = self.drop_piece(board, rot, bounds, x)

                if result is None:
                    continue

                new_board, lines = result

                score = self.evaluate(new_board, lines)

                moves.append((score, x, r, new_board))

        return moves

    # ---------------------------------------------------------

    def best_move(self, board, queue):

        piece = queue[0]

        best = None
        best_score = -1e9

        moves = self.possible_moves(board, piece)

        for score, x, r, new_board in moves:

            total_score = score

            if len(queue) > 1:

                next_piece = queue[1]

                future = self.possible_moves(new_board, next_piece)

                if future:
                    total_score += max(f[0] for f in future)

            if total_score > best_score:
                best_score = total_score
                best = (x, r, new_board)

        return best

    # ---------------------------------------------------------

    def generate_keys(self, piece, move):

        x, rot, _ = move

        shape = PIECES[piece][rot]

        min_x, _, _, _ = self.bounds[piece][rot]

        spawn_box = shape.shape[1]
        spawn_x = (BOARD_W - spawn_box) // 2
        spawn_x += min_x

        diff = x - spawn_x

        keys = []

        for _ in range(rot):
            keys.append("flecha_arr")

        if diff < 0:
            keys += ["flecha_izq"] * abs(diff)
        else:
            keys += ["flecha_der"] * diff

        keys.append("espacio")

        return keys

    # ---------------------------------------------------------

    def compute(self, state):

        queue = state["queue"]

        if queue == self.last_queue:
            return None

        self.last_queue = queue.copy()

        piece = queue[0]

        print("PIEZA:", piece)

        move = self.best_move(self.board, queue)

        if move is None:
            return None

        x, r, new_board = move

        self.board = new_board

        return self.generate_keys(piece, move)

    # ---------------------------------------------------------

    def print_board(self):

        print("\nTABLERO SIMULADO\n")

        for row in self.board:
            print(" ".join("█" if c else "." for c in row))

        print("-"*25)

# ──────────────────────────────────────────────────────────
#  ENVIRONMENT  —  Rediseñado para detectar posición real
# ──────────────────────────────────────────────────────────

class Environment:

    def __init__(self):

        # Crear mss una sola vez
        self.sct = mss.mss()

        # Colores del tablero
        self.HEX_L      = "#b76635"
        self.HEX_L_INV  = "#503fa5"
        self.HEX_S      = "#82b231"
        self.HEX_S_INV  = "#b9383f"
        self.HEX_P      = "#31b282"
        self.HEX_C      = "#b49a33"
        self.HEX_T      = "#a43e9b"

        self.color_map = {
            self.hex_to_rgb(self.HEX_L):     "L",
            self.hex_to_rgb(self.HEX_L_INV): "LI",
            self.hex_to_rgb(self.HEX_S):     "S",
            self.hex_to_rgb(self.HEX_S_INV): "SI",
            self.hex_to_rgb(self.HEX_P):     "P",
            self.hex_to_rgb(self.HEX_C):     "C",
            self.hex_to_rgb(self.HEX_T):     "T"
        }

        self.NEXT  = {'top': 277, 'left': 3708, 'width': 161, 'height': 484}
        self.HOLD  = {'top': 281, 'left': 3194, 'width': 161, 'height': 94}

    # -----------------------------------------------------

    def seleccionar_area(self, nombre, imagen):

        r = cv2.selectROI(nombre, imagen, False, False)
        cv2.destroyWindow(nombre)

        x, y, w, h = r

        return {"top": int(y), "left": int(x), "width": int(w), "height": int(h)}

    # -----------------------------------------------------

    def hex_to_rgb(self, hex_color):

        hex_color = hex_color.lstrip('#')

        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # -----------------------------------------------------

    def capturar_region(self, region):

        img = np.array(self.sct.grab(region))

        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # -----------------------------------------------------

    def screenshot(self):

        monitor = self.sct.monitors[0]

        img = np.array(self.sct.grab(monitor))

        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # -----------------------------------------------------

    def analizar_grid(self, img, filas, columnas, color_map_param=None):

        if color_map_param is None:
            color_map_param = self.color_map

        h, w, _ = img.shape

        cell_h = h // filas
        cell_w = w // columnas

        matriz = []

        for f in range(filas):

            fila = []

            y1 = f * cell_h
            y2 = (f + 1) * cell_h

            for c in range(columnas):

                x1 = c * cell_w
                x2 = (c + 1) * cell_w

                celda = img[y1:y2, x1:x2]

                found_color = None

                pixels = celda.reshape(-1,3)

                for b_ch, g_ch, r_ch in pixels:

                    rgb = (int(r_ch), int(g_ch), int(b_ch))

                    piece = color_map_param.get(rgb)

                    if piece:
                        found_color = piece
                        break

                fila.append(found_color if found_color else ".")

            matriz.append(fila)

        return matriz

    # -----------------------------------------------------

    def percept(self):

        next_img = self.capturar_region(self.NEXT)
        hold_img = self.capturar_region(self.HOLD)

        next_grid = self.analizar_grid(next_img, 5, 1)
        hold_grid = self.analizar_grid(hold_img, 1, 1)

        queue = [p[0] for p in next_grid if p[0] != "."]
        hold  = hold_grid[0][0]

        return {
            "queue": queue,
            "hold": hold
        }


# ──────────────────────────────────────────────────────────
#  EJECUCIÓN DE TECLAS
# ──────────────────────────────────────────────────────────

KEY_MAP = {
    "flecha_izq": "left",
    "flecha_der": "right",
    "flecha_arr": "up",
    "espacio":    "space",
    "c":          "c"
}

def ejecutar_movimiento(keys):

    for k in keys:
        pyautogui.press(KEY_MAP[k])
    time.sleep(0.02)

# ──────────────────────────────────────────────────────────
#  MAIN LOOP
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":

    env   = Environment()
    agent = Agent()

    print("=== Tetris Agent ===")
    print("Detectando piezas...")

    last_queue = None
    pending_move = None

    while True:

        try:

            state = env.percept()

            queue = state["queue"]

            if queue != last_queue:

                last_queue = queue.copy()

                if pending_move:
                    ejecutar_movimiento(pending_move)

                pending_move = agent.compute(state)

                agent.print_board()

            else:
                time.sleep(0.01)

        except Exception as e:

            print("[ERROR]", e)
            time.sleep(0.1)
