from browser import document, html, timer
import random, math

ROWS, COLS = 10, 10
CELL_SIZE = 60
WIDTH, HEIGHT = 600, 600

snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

players = []
current_player = 0
colors = ["red", "blue", "green", "purple"]

info_text = document["info-text"]

def get_position_coords(pos):
    if pos < 1: pos = 1
    if pos > 100: pos = 100
    row = (pos - 1) // COLS
    col = (pos - 1) % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = HEIGHT - (row * CELL_SIZE + CELL_SIZE // 2)
    return x, y

def draw_board():
    ctx.clearRect(0, 0, WIDTH, HEIGHT)
    ctx.strokeStyle = "black"
    ctx.font = "12px Arial"
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c * CELL_SIZE, r * CELL_SIZE
            ctx.strokeRect(x, y, CELL_SIZE, CELL_SIZE)
            num = ROWS * COLS - (r * COLS + c)
            if r % 2 == 1:
                num = ROWS * COLS - (r * COLS + (COLS - 1 - c))
            ctx.fillText(str(num), x + 5, y + 15)

    # tangga (hijau)
    ctx.strokeStyle = "green"
    for start, end in ladders.items():
        x1, y1 = get_position_coords(start)
        x2, y2 = get_position_coords(end)
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()

    # ular (merah)
    ctx.strokeStyle = "red"
    for start, end in snakes.items():
        x1, y1 = get_position_coords(start)
        x2, y2 = get_position_coords(end)
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()

    # pion pemain
    for i, pos in enumerate(players):
        x, y = get_position_coords(pos)
        ctx.beginPath()
        ctx.arc(x, y, 10, 0, 2 * math.pi)
        ctx.fillStyle = colors[i]
        ctx.fill()

def draw_dice(value):
    ctx.fillStyle = "white"
    ctx.fillRect(500, 20, 80, 80)
    ctx.strokeStyle = "black"
    ctx.strokeRect(500, 20, 80, 80)
    ctx.fillStyle = "black"
    ctx.font = "40px Arial"
    ctx.fillText(str(value), 530, 70)

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

        if elapsed["time"] >= 1500:  # berhenti animasi
            timer.clear_interval(dice_anim_timer)
            final_roll = random.randint(1, 6)
            draw_dice(final_roll)
            move_piece(final_roll)
            roll_button.disabled = False

    dice_anim_timer = timer.set_interval(update, 100)

def move_piece(steps):
    global current_player
    pos = players[current_player]
    for _ in range(steps):
        pos += 1
        if pos > 100: 
            pos = 100
        players[current_player] = pos
        draw_board()

    if pos in snakes:
        players[current_player] = snakes[pos]
    elif pos in ladders:
        players[current_player] = ladders[pos]

    draw_board()

    if players[current_player] == 100:
        info_text.textContent = f"🎉 Pemain {current_player+1} MENANG!"
        document["roll-button"].style.display = "none"
        return

    current_player = (current_player + 1) % len(players)
    info_text.textContent = f"Giliran Pemain {current_player+1}"

def start_game(num_players):
    global players, current_player
    players = [1] * num_players
    current_player = 0
    draw_board()
    draw_dice(1)
    info_text.textContent = f"Giliran Pemain 1"
    document["roll-button"].style.display = "inline-block"
    document["player-select-div"].style.display = "none"

# binding tombol pilih pemain
for btn in document.select(".player-btn"):
    btn.bind("click", lambda ev, n=int(btn.value): start_game(n))

document["roll-button"].bind("click", animate_dice)
