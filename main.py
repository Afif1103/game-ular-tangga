# main.py (Brython)
from browser import document, html, timer
import random, math

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

# ===== Konfigurasi papan =====
board_size = 10
cell_size = canvas.width // board_size

# Tangga (naik) dan Ular (turun)
ladders = {3: 22, 5: 8, 11: 26, 20: 29}
snakes  = {27: 1, 21: 9, 17: 4, 19: 7}

# ===== Data pemain =====
players = []
player_colors = ["red", "blue", "green", "orange"]
current_player = 0
positions = []
game_started = False

# ===== Gambar papan =====
def draw_board():
    ctx.fillStyle = "white"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.strokeStyle = "black"
    ctx.lineWidth = 1

    for row in range(board_size):
        for col in range(board_size):
            x = col * cell_size
            y = (board_size - 1 - row) * cell_size
            ctx.strokeRect(x, y, cell_size, cell_size)
            num = row * board_size + (col+1 if row % 2 == 0 else board_size-col)
            ctx.fillStyle = "black"
            ctx.font = "12px Arial"
            ctx.fillText(str(num), x+5, y+15)

    # gambar tangga
    ctx.strokeStyle = "green"
    ctx.lineWidth = 3
    for start, end in ladders.items():
        (x1, y1) = cell_center(start)
        (x2, y2) = cell_center(end)
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
        draw_arrow(x1, y1, x2, y2, "green")

    # gambar ular
    ctx.strokeStyle = "brown"
    ctx.lineWidth = 3
    for start, end in snakes.items():
        (x1, y1) = cell_center(start)
        (x2, y2) = cell_center(end)
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
        draw_arrow(x1, y1, x2, y2, "brown")

def draw_arrow(x1, y1, x2, y2, color):
    ctx.fillStyle = color
    angle = math.atan2(y2-y1, x2-x1)
    size = 10
    ctx.beginPath()
    ctx.moveTo(x2, y2)
    ctx.lineTo(x2 - size*math.cos(angle-math.pi/6),
               y2 - size*math.sin(angle-math.pi/6))
    ctx.lineTo(x2 - size*math.cos(angle+math.pi/6),
               y2 - size*math.sin(angle+math.pi/6))
    ctx.closePath()
    ctx.fill()

def cell_center(num):
    row = (num-1)//board_size
    col = (num-1)%board_size if row%2==0 else board_size-1-(num-1)%board_size
    x = col*cell_size + cell_size//2
    y = (board_size-1-row)*cell_size + cell_size//2
    return (x, y)

# ===== Dadu =====
def draw_dice(value):
    ctx.fillStyle = "white"
    ctx.fillRect(500, 20, 80, 80)
    ctx.strokeStyle = "black"
    ctx.strokeRect(500, 20, 80, 80)

    dot_positions = {
        1: [(540, 60)],
        2: [(520, 40), (560, 80)],
        3: [(520, 40), (540, 60), (560, 80)],
        4: [(520, 40), (520, 80), (560, 40), (560, 80)],
        5: [(520, 40), (520, 80), (560, 40), (560, 80), (540, 60)],
        6: [(520, 40), (520, 60), (520, 80),
            (560, 40), (560, 60), (560, 80)]
    }

    ctx.fillStyle = "black"
    for (x, y) in dot_positions[value]:
        ctx.beginPath()
        ctx.arc(x, y, 6, 0, 2*math.pi)
        ctx.fill()

dice_anim_timer = None
def animate_dice(ev):
    global dice_anim_timer, current_player
    roll_button = document["roll-button"]
    roll_button.disabled = True
    elapsed = {"time": 0}

    def update():
        elapsed["time"] += 100
        value = random.randint(1, 6)
        draw_dice(value)
        if elapsed["time"] >= 1500:
            timer.clear_interval(dice_anim_timer)
            final_roll = random.randint(1, 6)
            draw_dice(final_roll)
            move_piece(final_roll)
            roll_button.disabled = False

    dice_anim_timer = timer.set_interval(update, 100)

# ===== Gerak pion =====
def draw_players():
    for i, pos in enumerate(positions):
        (x, y) = cell_center(pos if pos > 0 else 1)
        offset = i*10
        ctx.beginPath()
        ctx.arc(x+offset-10, y, 10, 0, 2*math.pi)
        ctx.fillStyle = player_colors[i]
        ctx.fill()

def move_piece(roll):
    global current_player
    pos = positions[current_player]
    pos += roll
    if pos > 100:
        pos = 100 - (pos-100)
    if pos in ladders: pos = ladders[pos]
    if pos in snakes: pos = snakes[pos]
    positions[current_player] = pos

    # cek menang
    if pos == 100:
        document["info-text"].text = f"Pemain {current_player+1} MENANG!"
        document["roll-button"].disabled = True
        return

    # giliran berikutnya
    current_player = (current_player+1) % len(players)
    document["info-text"].text = f"Giliran Pemain {current_player+1}"

    draw_board()
    draw_players()

# ===== Setup =====
def start_game(num_players):
    global players, positions, game_started
    players = list(range(num_players))
    positions = [0]*num_players
    game_started = True
    draw_board()
    draw_players()
    document["info-text"].text = f"Giliran Pemain 1"
    document["roll-button"].style.display = "inline-block"
    document["player-select-div"].style.display = "none"

# tombol pilih pemain
for btn in document.select(".player-btn"):
    def handler(ev, btn=btn):
        num = int(btn.attrs["value"])
        start_game(num)
    btn.bind("click", handler)

document["roll-button"].bind("click", animate_dice)

# gambar awal
draw_board()
