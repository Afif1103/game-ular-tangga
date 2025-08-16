from browser import document, html, timer
import random
import math

# --- Setup Elemen HTML dan Canvas ---
canvas = document["game-canvas"]
ctx = canvas.getContext("2d")
info_text = document["info-text"]
roll_button = document["roll-button"]
player_select_div = document["player-select-div"]
player_buttons = document.select(".player-btn")

# --- Konstanta Global ---
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH // COLS

def rgb_to_css(rgb_tuple):
    return f"rgb({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]})"

WHITE, BLACK, RED, GREEN, BLUE, YELLOW, DARK = map(rgb_to_css, [
    (255, 255, 255), (0, 0, 0), (220, 60, 60), (60, 200, 60),
    (60, 60, 220), (220, 200, 60), (40, 40, 40)
])

PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]
snakes  = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

# --- State Permainan (dengan state untuk semua animasi) ---
game_state = {
    "num_players": 0, "positions": [], "turn": 0, "winner": None,
    "dice_result": 1, "is_animating": False,
    "animation_start_time": 0, "last_flicker_time": 0,
    "steps_to_move": 0, "move_animation_id": None
}

# --- Fungsi Utilitas & Menggambar (Tidak ada perubahan) ---
def get_pos(square):
    if square < 1: square = 1;
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
    left  = (base_x - uy * head_w, base_y + ux * head_w); right = (base_x + uy * head_w, base_y - ux * head_w)
    ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(left[0], left[1]); ctx.lineTo(right[0], right[1]); ctx.closePath(); ctx.fillStyle = color; ctx.fill()

def draw_board():
    ctx.fillStyle = WHITE; ctx.fillRect(0, 0, WIDTH, HEIGHT)
    ctx.font = "18px Arial"; ctx.textAlign = "left"; ctx.textBaseline = "top"
    for r in range(ROWS):
        for c in range(COLS):
            rect_x, rect_y = c * CELL_SIZE, r * CELL_SIZE
            draw_row = ROWS - 1 - r
            base = draw_row * COLS
            num = base + c + 1 if draw_row % 2 == 0 else base + (COLS - 1 - c) + 1
            ctx.strokeStyle = BLACK; ctx.lineWidth = 1; ctx.strokeRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
            ctx.fillStyle = BLACK; ctx.fillText(str(num), rect_x + 4, rect_y + 4)
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
    dots = {1: [(40, 40)], 2: [(20, 20), (60, 60)], 3: [(20, 20), (40, 40), (60, 60)], 4: [(20, 20), (60, 20), (20, 60), (60, 60)], 5: [(20, 20), (60, 20), (40, 40), (20, 60), (60, 60)], 6: [(20, 20), (60, 20), (20, 40), (60, 40), (20, 60), (60, 60)]}
    if value in dots:
        for px, py in dots[value]:
            ctx.beginPath(); ctx.arc(x_base + px, y_base + py, 6, 0, 2 * math.pi); ctx.fillStyle = BLACK; ctx.fill()

# --- Logika Permainan & Animasi ---
def redraw_all():
    draw_board(); draw_players(); draw_dice(game_state["dice_result"]); update_info_text()

def update_info_text():
    if game_state["winner"] is not None:
        info_text.textContent = f"🎉 Player {game_state['winner'] + 1} MENANG!"
    else: info_text.textContent = f"Giliran Player {game_state['turn'] + 1}"

# --- ANIMASI PERGERAKAN PION (BARU) ---
def move_one_step():
    """Fungsi yang dipanggil berulang kali untuk menggerakkan pion satu kotak."""
    player_idx = game_state["turn"]
    # Hentikan jika sudah selesai melangkah atau mencapai 100
    if game_state["steps_to_move"] <= 0 or game_state["positions"][player_idx] >= 100:
        finish_move()
        return

    game_state["positions"][player_idx] += 1
    game_state["steps_to_move"] -= 1
    redraw_all()

def finish_move():
    """Dijalankan setelah pion selesai bergerak per kotak."""
    timer.clear_interval(game_state["move_animation_id"])
    player_idx = game_state["turn"]
    current_pos = game_state["positions"][player_idx]

    # Cek ular atau tangga
    if current_pos in snakes:
        game_state["positions"][player_idx] = snakes[current_pos]
    elif current_pos in ladders:
        game_state["positions"][player_idx] = ladders[current_pos]
    
    # Gambar ulang untuk menunjukkan posisi akhir (setelah ular/tangga)
    redraw_all()
    
    # Cek kemenangan
    if game_state["positions"][player_idx] >= 100:
        game_state["positions"][player_idx] = 100
        game_state["winner"] = player_idx
    else:
        # Ganti giliran
        game_state["turn"] = (game_state["turn"] + 1) % game_state["num_players"]
    
    game_state["is_animating"] = False
    roll_button.disabled = False
    redraw_all() # Gambar ulang terakhir untuk update info text giliran/pemenang

# --- ANIMASI DADU ---
def animation_loop(timestamp):
    """Loop utama animasi dadu."""
    if not game_state["is_animating"]: return
    elapsed_time = timestamp - game_state["animation_start_time"]
    if elapsed_time > 1500:
        finish_roll()
        return
    time_since_flicker = timestamp - game_state["last_flicker_time"]
    if time_since_flicker > 100:
        game_state["dice_result"] = random.randint(1, 6)
        game_state["last_flicker_time"] = timestamp
        redraw_all()
    timer.request_animation_frame(animation_loop)

def finish_roll():
    """Menyelesaikan lemparan dadu dan MEMULAI animasi pergerakan pion."""
    rolled_value = random.randint(1, 6)
    game_state["dice_result"] = rolled_value
    game_state["steps_to_move"] = rolled_value
    redraw_all() # Tampilkan hasil dadu final
    
    # Mulai animasi pergerakan pion
    game_state["move_animation_id"] = timer.set_interval(move_one_step, 220)

# --- FUNGSI UTAMA & EVENT HANDLER ---
def handle_roll(event):
    """Memulai animasi dadu."""
    if game_state["is_animating"] or game_state["winner"] is not None: return
    game_state["is_animating"] = True
    roll_button.disabled = True
    game_state["animation_start_time"] = timer.perf_counter()
    game_state["last_flicker_time"] = game_state["animation_start_time"]
    timer.request_animation_frame(animation_loop)

def start_game(event):
    """Memulai permainan."""
    num = int(event.target.value)
    game_state["num_players"] = num; game_state["positions"] = [1] * num
    player_select_div.style.display = "none"; roll_button.style.display = "inline-block"
    redraw_all()

# --- Ikat Event dan Gambar Papan Awal ---
roll_button.bind("click", handle_roll)
for btn in player_buttons: btn.bind("click", start_game)
draw_board()
