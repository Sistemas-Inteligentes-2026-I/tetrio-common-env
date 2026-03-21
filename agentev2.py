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

        self.bounds = {}

        for p, rots in PIECES.items():
            self.bounds[p] = []
            for r in rots:
                ys, xs = np.where(r)
                self.bounds[p].append((xs.min(), xs.max(), ys.min(), ys.max()))

    # ---------------------------------------------------------

    def holes(self, board):

        holes = 0

        for x in range(BOARD_W):

            col = board[:,x]
            filled = np.where(col)[0]

            if filled.size:
                holes += np.sum(col[filled[0]:] == 0)

        return holes

    # ---------------------------------------------------------

    def column_heights(self, board):

        heights = np.zeros(BOARD_W)

        for x in range(BOARD_W):

            col = board[:,x]
            filled = np.where(col)[0]

            if filled.size:
                heights[x] = BOARD_H - filled[0]

        return heights

    # ---------------------------------------------------------

    def clear_lines(self, board):

        full = np.all(board,axis=1)
        lines = np.sum(full)

        if lines:
            board = board[~full]
            board = np.vstack((np.zeros((lines,BOARD_W)),board))

        return board,lines

    # ---------------------------------------------------------

    def drop_height(self, board, piece, bounds, x):

        min_x, max_x, min_y, max_y = bounds

        drop_y = BOARD_H - (max_y - min_y + 1)

        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):
                if piece[py][px]:
                    bx = x + px - min_x
                    if bx < 0 or bx >= BOARD_W:
                        return -1
                    col = board[:, bx]
                    filled = np.where(col)[0]
                    if filled.size:
                        top = filled[0] - 1
                    else:
                        top = BOARD_H - 1
                    required_y = top - (py - min_y)
                    if required_y < drop_y:
                        drop_y = required_y

        return drop_y if drop_y >= 0 else -1

    # ---------------------------------------------------------

    def drop_piece(self, board, piece, bounds, x):

        y = self.drop_height(board, piece, bounds, x)

        if y < 0:
            return None

        new = board.copy()

        min_x, max_x, min_y, max_y = bounds

        for py in range(min_y, max_y + 1):
            for px in range(min_x, max_x + 1):
                if piece[py][px]:
                    bx = x + px - min_x
                    by = y + py - min_y
                    new[by][bx] = 1

        new, lines = self.clear_lines(new)

        return new, lines

    # ---------------------------------------------------------
    # FULL CLEAR SEARCH
    # ---------------------------------------------------------

    def heuristic(self, board):

        heights = self.column_heights(board)
        holes = self.holes(board)

        bump = np.sum(np.abs(np.diff(heights)))

        # Prioridad máxima a full clears
        if holes == 0 and np.sum(heights) == 0:
            return 10000  # Bonus enorme para tablero vacío

        score = (
            -holes * 100
            -np.sum(heights) * 0.3
            -bump * 0.2
        )

        return score
    
    def beam_search(self, board, queue, beam_width=8):

        states = [(board, [], 0)]  
        # (board, moves, score)

        for depth, piece in enumerate(queue):

            next_states = []

            for board_state, moves, score in states:

                for r,rot in enumerate(PIECES[piece]):

                    bounds = self.bounds[piece][r]
                    min_x,max_x,_,_ = bounds

                    for x in range(-min_x, BOARD_W-max_x):

                        result = self.drop_piece(board_state,rot,bounds,x)

                        if result is None:
                            continue

                        new_board,lines = result

                        new_score = score + self.heuristic(new_board) + lines*10

                        new_moves = moves + [(x,r)]

                        next_states.append((new_board,new_moves,new_score))

                        # FULL CLEAR encontrado
                        if not np.any(new_board):
                            return new_moves

            # ordenar por score y quedarnos con los mejores
            next_states.sort(key=lambda s:s[2], reverse=True)

            states = next_states[:beam_width]

            if not states:
                break

        if states:
            return states[0][1]

        return None
    
    def best_move(self, board, queue):

        moves = self.beam_search(board, queue)

        if not moves:
            return None

        x,r = moves[0]

        result = self.drop_piece(board, PIECES[queue[0]][r], self.bounds[queue[0]][r], x)

        if result is None:
            return None

        new_board,_ = result

        return (x,r,new_board)

    # ---------------------------------------------------------

    def generate_keys(self,piece,move):

        x,rot,_ = move

        shape = PIECES[piece][rot]

        min_x,_,_,_ = self.bounds[piece][rot]

        spawn_box = shape.shape[1]
        spawn_x = (BOARD_W-spawn_box)//2 + min_x

        diff = x-spawn_x

        keys=[]

        keys += ["up"]*rot

        if diff<0:
            keys += ["left"]*abs(diff)
        else:
            keys += ["right"]*diff

        keys.append("space")

        return keys

    # ---------------------------------------------------------

    def compute(self,state):

        queue = state["queue"]

        if queue == self.last_queue:
            return None

        self.last_queue = queue.copy()

        move = self.best_move(self.board,queue)

        if move is None:
            return None

        x,r,new_board = move

        self.board = new_board

        return self.generate_keys(queue[0],move)

# ──────────────────────────────────────────────────────────
#  ENVIRONMENT  —  Rediseñado para detectar posición real
# ──────────────────────────────────────────────────────────

class Environment:

    def __init__(self):

        self.sct = mss.mss()

        self.color_map = {
            (194,115,66):"L",
            (91,74,175):"LI",
            (142,191,61):"S",
            (194,63,70):"SI",
            (61,147,114):"P",
            (146,129,61):"C",
            (176,76,166):"T"
        }

        self.NEXT = {'top':277,'left':3708,'width':161,'height':484}
        self.HOLD = {'top':281,'left':3194,'width':161,'height':94}

    def color_match(self, rgb):

        r,g,b = rgb

        for (cr,cg,cb),p in self.color_map.items():

            if abs(r-cr)<=30 and abs(g-cg)<=30 and abs(b-cb)<=30:

                return p

        return None

    def detectar_next(self,img):

        h,w,_=img.shape

        slot_h=h//5

        queue=[]

        for i in range(5):

            y=int((i+0.6)*slot_h)
            x=w//2

            b,g,r,_=img[y,x]

            piece=self.color_match((int(r),int(g),int(b)))

            if piece:
                queue.append(piece)

        return queue

    def detectar_hold(self,img):

        h,w,_=img.shape

        y=int(h*0.6)
        x=w//2

        b,g,r,_=img[y,x]

        piece=self.color_match((int(r),int(g),int(b)))

        return piece if piece else "."

    def percept(self):

        next_img=np.array(self.sct.grab(self.NEXT))
        hold_img=np.array(self.sct.grab(self.HOLD))

        queue=self.detectar_next(next_img)
        hold=self.detectar_hold(hold_img)

        return {"queue":queue,"hold":hold}


# ============================================================
# INPUT
# ============================================================

def ejecutar_movimiento(keys):

    if keys:
        pyautogui.press(keys, interval=0.02)

# ============================================================
# MAIN
# ============================================================

if __name__=="__main__":

    env=Environment()
    agent=Agent()

    print("=== Tetris Agent ===")

    last_queue=None
    pending_move=None

    while True:

        state=env.percept()

        queue=state["queue"]

        if len(queue)<5:
            continue

        if queue!=last_queue:

            last_queue=queue

            if pending_move:
                ejecutar_movimiento(pending_move)

            pending_move=agent.compute(state)