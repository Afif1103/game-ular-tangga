from browser import document, html, timer
import random

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

ROWS, COLS = 10, 10
CELL_SIZE = canvas.width // COLS

# pemain
player_count = 0
players = []
player_colors = ["red", "blue", "green", "purple"]
positions = []

# giliran
turn = 0
rolling = False

# ular dan tangga
snakes = {16: 6, 48: 26, 62: 18, 88: 24, 95: 56, 97: 78}
ladders = {1: 38, 4: 14, 9: 31, 28: 84, 21: 42, 51: 67, 72: 91, 80: 99}

# --- gambar papan ---
def draw_board():
    ctx.clearRect(0,0,canvas.width,canvas.height)
    num = 1
    for r in range(ROWS):
        for c in range(COLS):
            row = r
            if row % 2 == 0:
                col = c
            else:
                col = COLS - 1 - c

            x = col * CELL_SIZE
            y = (ROWS-1-r) * CELL_SIZE   # penting! mulai dari bawah

            # warna kotak
            if (r+c) % 2 == 0:
                ctx.fillStyle = "#fffacd"
            else:
                ctx.fillStyle = "#e6e6fa"
            ctx.fillRect(x,y,CELL_SIZE,CELL_SIZE)

            ctx.strokeStyle = "black"
            ctx.strokeRect(x,y,CELL_SIZE,CELL_SIZE)

            # nomor
            ctx.fillStyle = "black"
            ctx.font = "12px Arial"
            ctx.fillText(str(num), x+3, y+12)
            num += 1

    # tangga
    ctx.strokeStyle = "green"
    ctx.lineWidth = 5
    for start,end in ladders.items():
        x1,y1 = cell_center(start)
        x2,y2 = cell_center(end)
        ctx.beginPath()
        ctx.moveTo(x1,y1)
        ctx.lineTo(x2,y2)
        ctx.stroke()

    # ular
    ctx.strokeStyle = "brown"
    ctx.lineWidth = 5
    for head,tail in snakes.items():
        x1,y1 = cell_center(head)
        x2,y2 = cell_center(tail)
        ctx.beginPath()
        ctx.moveTo(x1,y1)
        ctx.lineTo(x2,y2)
        ctx.stroke()

# --- posisi kotak ---
def cell_center(n):
    row = (n-1) // COLS
    col = (n-1) % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    x = col * CELL_SIZE + CELL_SIZE//2
    y = (ROWS-1-row) * CELL_SIZE + CELL_SIZE//2
    return (x,y)

# --- gambar pion ---
def draw_players():
    for i,pos in enumerate(positions):
        if pos < 1: continue
        x,y = cell_center(pos)
        offset = (i-1.5)*10
        ctx.beginPath()
        ctx.arc(x+offset,y,10,0,6.28)
        ctx.fillStyle = player_colors[i]
        ctx.fill()
        ctx.stroke()

# --- giliran ---
def next_turn():
    global turn
    turn = (turn+1) % player_count
    document["info-text"].text = f"Giliran Pemain {turn+1}"

# --- lempar dadu ---
def roll_dice(ev):
    global rolling
    if rolling: return
    rolling = True
    steps = random.randint(15,25)   # animasi acak
    def animate(count):
        if count==0:
            finish_roll()
            return
        val = random.randint(1,6)
        document["info-text"].text = f"Pemain {turn+1} lempar: {val}"
        timer.set_timeout(lambda: animate(count-1),100)
    animate(steps)

def finish_roll():
    global rolling
    val = random.randint(1,6)
    document["info-text"].text = f"Pemain {turn+1} dapat {val}"
    positions[turn] += val
    if positions[turn] in ladders:
        positions[turn] = ladders[positions[turn]]
    elif positions[turn] in snakes:
        positions[turn] = snakes[positions[turn]]
    if positions[turn] >= 100:
        document["info-text"].text = f"Pemain {turn+1} MENANG!"
        document["roll-button"].disabled = True
    else:
        next_turn()
    draw_board()
    draw_players()
    rolling = False

# --- pilih pemain ---
def choose_players(ev):
    global player_count, players, positions
    player_count = int(ev.target.value)
    positions = [0]*player_count
    document["player-select-div"].style.display = "none"
    document["roll-button"].style.display = "inline-block"
    document["info-text"].text = "Giliran Pemain 1"
    draw_board()
    draw_players()

# --- event ---
for btn in document.select(".player-btn"):
    btn.bind("click", choose_players)

document["roll-button"].bind("click", roll_dice)

# awal
draw_board()
