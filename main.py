from browser import document, html
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

# Helper untuk konversi warna
def rgb_to_css(rgb_tuple):
    return f"rgb({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]})"

# Definisi Warna (sudah dalam format CSS)
WHITE = rgb_to_css((255, 255, 255))
BLACK = rgb_to_css((0, 0, 0))
RED = rgb_to_css((220, 60, 60))
GREEN = rgb_to_css((60, 200, 60))
BLUE = rgb_to_css((60, 60, 220))
YELLOW = rgb_to_css((220, 200, 60))
DARK = rgb_to_css((40, 40, 40))

PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]
snakes  = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

# --- State Permainan (Variabel Global) ---
game_state = {
    "num_players": 0,
    "positions": [],
    "turn": 0,
    "winner": None,
    "dice_result": None
}

# --- Fungsi Utilitas (Sama seperti Pygame) ---
def get_pos(square):
    if square < 1: square = 1
    if square > 100: square = 100
    square -= 1
    row = square // COLS
    col = square % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = (ROWS - 1 - row) * CELL_SIZE + CELL_SIZE // 2
    return x, y

# --- Fungsi Menggambar (Ditulis Ulang untuk Canvas) ---
def draw_arrowhead(tip, tail, color):
    tx, ty = tip
    sx, sy = tail
    dx, dy = tx - sx, ty - sy
    L = math.hypot(dx, dy)
    if L == 0: return
    ux, uy = dx / L, dy / L
    head_len = 20
    head_w = 10
    base_x = tx - ux * head_len
    base_y = ty - uy * head_len
    left  = (base_x - uy * head_w, base_y + ux * head_w)
    right = (base_x + uy * head_w, base_y - ux * head_w)

    ctx.beginPath()
    ctx.moveTo(tx, ty)
    ctx.lineTo(left[0], left[1])
    ctx.lineTo(right[0], right[1])
    ctx.closePath()
    ctx.fillStyle = color
    ctx.fill()

def draw_board():
    ctx.fillStyle = WHITE
    ctx.fillRect(0, 0, WIDTH, HEIGHT)
    ctx.font = "18px Arial"
    ctx.textAlign = "left"
    ctx.textBaseline = "top"

    for r in range(ROWS):
        for c in range(COLS):
            rect_x, rect_y = c * CELL_SIZE, r * CELL_SIZE
            draw_row = ROWS - 1 - r
            base = draw_row * COLS
            if draw_row % 2 == 0:
                num = base + c + 1
            else:
                num = base + (COLS - 1 - c) + 1
            
            ctx.strokeStyle = BLACK
            ctx.lineWidth = 1
            ctx.strokeRect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
            
            ctx.fillStyle = BLACK
            ctx.fillText(str(num), rect_x + 4, rect_y + 4)

    for start, end in snakes.items():
        sx, sy = get_pos(start)
        ex, ey = get_pos(end)
        ctx.beginPath()
        ctx.moveTo(sx, sy)
        ctx.lineTo(ex, ey)
        ctx.strokeStyle = RED
        ctx.lineWidth = 8
        ctx.stroke()
        draw_arrowhead((ex, ey), (sx, sy), RED)

    for start, end in ladders.items():
        sx, sy = get_pos(start)
        ex, ey = get_pos(end)
        ctx.beginPath()
        ctx.moveTo(sx, sy)
        ctx.lineTo(ex, ey)
        ctx.strokeStyle = GREEN
        ctx.lineWidth = 8
        ctx.stroke()
        draw_arrowhead((ex, ey), (sx, sy), GREEN)

def draw_players():
    offsets = [(0, 0), (8, 8), (-8, 8), (8, -8)]
    for i, sq in enumerate(game_state["positions"]):
        x, y = get_pos(sq)
        ox, oy = offsets[i] if i < len(offsets) else (0, 0)
        
        ctx.beginPath()
        ctx.arc(x + ox, y + oy, 12, 0, 2 * math.pi)
        ctx.fillStyle = PLAYER_COLORS[i]
        ctx.fill()
        ctx.strokeStyle = DARK
        ctx.lineWidth = 2
        ctx.stroke()

def draw_dice(value):
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)"
    ctx.fillRect(WIDTH - 100, 20, 80, 80)
    ctx.strokeStyle = BLACK
    ctx.lineWidth = 3
    ctx.strokeRect(WIDTH - 100, 20, 80, 80)
    
    ctx.font = "48px Arial"
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillStyle = BLACK
    ctx.fillText(str(value), WIDTH - 60, 60)

# --- Fungsi Utama Permainan ---
def redraw_all():
    """Menggambar ulang seluruh state permainan."""
    draw_board()
    draw_players()
    if game_state["dice_result"] is not None:
        draw_dice(game_state["dice_result"])
    update_info_text()

def update_info_text():
    """Memperbarui teks informasi di bawah papan."""
    if game_state["winner"] is not None:
        info_text.textContent = f"🎉 Player {game_state['winner'] + 1} MENANG!"
        roll_button.disabled = True
    else:
        info_text.textContent = f"Giliran Player {game_state['turn'] + 1}"

def move_player(player_idx, steps):
    """Memindahkan pemain (instan, tanpa animasi)."""
    current_pos = game_state["positions"][player_idx]
    target_pos = current_pos + steps
    
    if target_pos > 100:
        target_pos = 100 # Tidak melebihi 100
    
    game_state["positions"][player_idx] = target_pos
    
    # Cek ular atau tangga
    if target_pos in snakes:
        game_state["positions"][player_idx] = snakes[target_pos]
    elif target_pos in ladders:
        game_state["positions"][player_idx] = ladders[target_pos]

def handle_roll(event):
    """Dipanggil saat tombol 'Lempar Dadu' diklik."""
    if game_state["winner"] is not None:
        return

    rolled_value = random.randint(1, 6)
    game_state["dice_result"] = rolled_value
    
    move_player(game_state["turn"], rolled_value)
    
    # Cek kemenangan
    if game_state["positions"][game_state["turn"]] >= 100:
        game_state["positions"][game_state["turn"]] = 100
        game_state["winner"] = game_state["turn"]
    else:
        # Ganti giliran
        game_state["turn"] = (game_state["turn"] + 1) % game_state["num_players"]
    
    redraw_all()

def start_game(event):
    """Memulai permainan setelah jumlah pemain dipilih."""
    num = int(event.target.value)
    game_state["num_players"] = num
    game_state["positions"] = [1] * num
    
    player_select_div.style.display = "none"
    roll_button.style.display = "inline-block"
    
    redraw_all()

# --- Ikat Event ke Fungsi ---
roll_button.bind("click", handle_roll)
for btn in player_buttons:
    btn.bind("click", start_game)

# --- Gambar Papan Awal ---
draw_board()
