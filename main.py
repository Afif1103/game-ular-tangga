from browser import document, html, timer, window
import random
import math
import time

# ===== Benih acak =====
random.seed(time.time())

# ===== Elemen HTML =====
canvas = document["game-canvas"]
ctx = canvas.getContext("2d")
info_text = document["info-text"]
roll_button = document["roll-button"]
player_select_div = document["player-select-div"]
player_buttons = document.select(".player-btn")
question_div = document["question-div"]
answer_input = document["answer-input"]
submit_btn = document["submit-btn"]
player_names_div = document["player-names-div"]
name_inputs_div = document["name-inputs"]
start_game_btn = document["start-game-btn"]

# ===== Konstanta =====
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH // COLS

def rgb_to_css(rgb_tuple):
    return f"rgb({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]})"

WHITE, BLACK, RED, GREEN, BLUE, YELLOW, DARK = map(rgb_to_css, [
    (255, 255, 255), (0, 0, 0), (220, 60, 60), (60, 200, 60),
    (60, 60, 220), (220, 200, 60), (40, 40, 40)
])
CELL_COLOR_1 = "#fffacd"
CELL_COLOR_2 = "#e6e6fa"
PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]

snakes  = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {2: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

# ===== State Permainan =====
game_state = {
    "num_players": 0, "positions": [], "turn": 0, "winner": None,
    "dice_result": 1, "is_moving": False,
    "steps_to_move": 0, "move_animation_id": None,
    "expected_answer": 0, "player_names": []
}

# ===== Fungsi Utilitas =====
def get_pos(square):
    if square < 1: square = 1
    if square > 100: square = 100
    square -= 1
    row, col = square // COLS, square % COLS
    if row % 2 == 1: col = COLS - 1 - col
    x, y = col * CELL_SIZE + CELL_SIZE // 2, (ROWS - 1 - row) * CELL_SIZE + CELL_SIZE // 2
    return x, y

def draw_arrowhead(tip, tail, color):
    tx, ty = tip; sx, sy = tail; dx, dy = tx - sx, ty - sy
    L = math.hypot(dx, dy)
    if L == 0: return
    ux, uy = dx / L, dy / L
    head_len, head_w = 20, 10
    base_x, base_y = tx - ux * head_len, ty - uy * head_len
    left  = (base_x - uy * head_w, base_y + ux * head_w)
    right = (base_x + uy * head_w, base_y - ux * head_w)
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(left[0], left[1]); ctx.lineTo(right[0], right[1]); ctx.closePath()
    ctx.fillStyle = color; ctx.fill()

# ===== Menggambar papan & pemain =====
def draw_board():
    ctx.font = "18px Arial"; ctx.textAlign = "left"; ctx.textBaseline = "top"
    for r in range(ROWS):
        for c in range(COLS):
            draw_row = ROWS - 1 - r
            base = draw_row * COLS
            num = base + c + 1 if draw_row % 2 == 0 else base + (COLS - 1 - c) + 1
            rect_x, rect_y = c * CELL_SIZE, r * CELL_SIZE
            ctx.fillStyle = CELL_COLOR_1 if (r + c) % 2 == 0 else CELL_COLOR_2
            ctx.fillRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
            ctx.strokeStyle = BLACK; ctx.lineWidth = 1; ctx.strokeRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
            ctx.fillStyle = BLACK; ctx.fillText(str(num), rect_x + 5, rect_y + 5)
    for data, color in [(snakes, RED), (ladders, GREEN)]:
        for start, end in data.items():
            sx, sy = get_pos(start); ex, ey = get_pos(end)
            ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.strokeStyle = color; ctx.lineWidth = 8; ctx.stroke()
            draw_arrowhead((ex, ey), (sx, sy), color)

def draw_players():
    offsets = [(0, 0), (8, 8), (-8, 8), (8, -8)]
    for i, sq in enumerate(game_state["positions"]):
        x, y = get_pos(sq)
        ox, oy = offsets[i] if i < len(offsets) else (0, 0)
        ctx.beginPath(); ctx.arc(x + ox, y + oy, 12, 0, 2 * math.pi); ctx.fillStyle = PLAYER_COLORS[i]; ctx.fill()
        ctx.strokeStyle = DARK; ctx.lineWidth = 2; ctx.stroke()

def draw_dice(value):
    x_base, y_base = WIDTH - 100, 20
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)"; ctx.fillRect(x_base, y_base, 80, 80)
    ctx.strokeStyle = BLACK; ctx.lineWidth = 3; ctx.strokeRect(x_base, y_base, 80, 80)
    dots = {
        1: [(40,40)], 2: [(20,20),(60,60)], 3: [(20,20),(40,40),(60,60)],
        4: [(20,20),(60,20),(20,60),(60,60)], 5: [(20,20),(60,20),(40,40),(20,60),(60,60)],
        6: [(20,20),(60,20),(20,40),(60,40),(20,60),(60,60)]
    }
    for px, py in dots.get(value, []):
        ctx.beginPath(); ctx.arc(x_base + px, y_base + py, 6, 0, 2*math.pi); ctx.fillStyle = BLACK; ctx.fill()

def redraw_all():
    draw_board(); draw_players(); draw_dice(game_state["dice_result"]); update_info_text()

def update_info_text():
    if game_state["winner"] is not None:
        winner_name = game_state["player_names"][game_state["winner"]]
        info_text.textContent = f"🎉 {winner_name} MENANG!"
    else:
        current_name = game_state["player_names"][game_state["turn"]] if game_state["player_names"] else "Player"
        info_text.textContent = f"Giliran {current_name}"

# ===== Animasi pergerakan =====
def move_one_step():
    player_idx = game_state["turn"]
    if game_state["steps_to_move"] <= 0 or game_state["positions"][player_idx] >= 100:
        finish_move()
        return
    game_state["positions"][player_idx] += 1
    game_state["steps_to_move"] -= 1
    redraw_all()

def finish_move():
    timer.clear_interval(game_state["move_animation_id"])
    player_idx = game_state["turn"]
    current_pos = game_state["positions"][player_idx]
    if current_pos in snakes: game_state["positions"][player_idx] = snakes[current_pos]
    elif current_pos in ladders: game_state["positions"][player_idx] = ladders[current_pos]
    redraw_all()
    if game_state["positions"][player_idx] >= 100:
        game_state["positions"][player_idx] = 100
        game_state["winner"] = player_idx
    else:
        game_state["turn"] = (game_state["turn"] + 1) % game_state["num_players"]
    game_state["is_moving"] = False
    roll_button.disabled = False
    question_div.style.display = "none"
    redraw_all()

# ===== Logika pertanyaan =====
def handle_roll(event):
    if game_state["is_moving"] or game_state["winner"] is not None: return
    game_state["is_moving"] = True
    roll_button.disabled = True
    rolled_value = random.randint(1, 6)
    game_state["dice_result"] = rolled_value
    redraw_all()

    player_idx = game_state["turn"]
    current_pos = game_state["positions"][player_idx]
    game_state["expected_answer"] = rolled_value + current_pos

    question_div.style.display = "block"
    question_div.textContent = f"{game_state['player_names'][player_idx]}:---- Dadu {rolled_value}, Posisi sekarang: {current_pos}\nBerapa jumlahnya?"
    answer_input.value = ""

def check_answer(event):
    try:
        if int(answer_input.value) == game_state["expected_answer"]:
            game_state["steps_to_move"] = game_state["dice_result"]
            question_div.style.display = "none"
            timer.set_timeout(lambda: start_pawn_animation(), 200)
        else:
            window.alert(f"Salah! Jawaban yang benar: {game_state['expected_answer']}")
            finish_move()
    except:
        window.alert("Input tidak valid!")
        finish_move()

def start_pawn_animation():
    game_state["move_animation_id"] = timer.set_interval(move_one_step, 220)

# ===== Pemilihan nama pemain =====
def start_name_input(event):
    num = int(event.target.value)
    game_state["num_players"] = num
    player_select_div.style.display = "none"
    name_inputs_div.clear()
    for i in range(num):
        lbl = html.LABEL(f"Nama Player {i+1}: ")
        inp = html.INPUT(type="text", Id=f"player-name-{i}")
        name_inputs_div <= lbl + inp + html.BR()
    player_names_div.style.display = "block"

def start_game_with_names(event):
    game_state["positions"] = [1]*game_state["num_players"]
    game_state["player_names"] = []
    for i in range(game_state["num_players"]):
        inp = document[f"player-name-{i}"]
        name = inp.value.strip() or f"Player {i+1}"
        game_state["player_names"].append(name)
    player_names_div.style.display = "none"
    roll_button.style.display = "inline-block"
    redraw_all()

# ===== Event binding =====
for btn in player_buttons:
    btn.bind("click", start_name_input)
start_game_btn.bind("click", start_game_with_names)
roll_button.bind("click", handle_roll)
submit_btn.bind("click", check_answer)

draw_board()
