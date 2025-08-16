from browser import document, html, timer
import math, random

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

ROWS, COLS = 10, 10
CELL_SIZE = canvas.width // COLS

# ular & tangga
ladders = {3: 22, 5: 8, 11: 26, 20: 29, 27: 56, 21: 82, 43: 77, 50: 91, 57: 76, 72: 92}
snakes  = {17: 4, 19: 7, 54: 34, 62: 18, 64: 60, 87: 24, 93: 73, 95: 75, 98: 79}

players = []
player_pos = []
turn = 0
game_over = False

info_text = document["info-text"]
roll_button = document["roll-button"]
player_select_div = document["player-select-div"]

# posisi kotak → koordinat tengah
def cell_center(n):
    row = (n-1) // COLS
    col = (n-1) % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    x = col * CELL_SIZE + CELL_SIZE//2
    y = canvas.height - (row * CELL_SIZE + CELL_SIZE//2)
    return (x, y)

# gambar panah rapi
def draw_arrow(x1, y1, x2, y2, color, is_ladder=True):
    ctx.strokeStyle = color
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.stroke()

    angle = -math.pi/2 if is_ladder else math.pi/2
    size = 12
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.moveTo(x2, y2)
    ctx.lineTo(x2 - size*math.cos(angle-math.pi/6),
               y2 - size*math.sin(angle-math.pi/6))
    ctx.lineTo(x2 - size*math.cos(angle+math.pi/6),
               y2 - size*math.sin(angle+math.pi/6))
    ctx.closePath()
    ctx.fill()

# gambar papan
def draw_board():
    ctx.clearRect(0,0,canvas.width,canvas.height)
    num = 100
    for r in range(ROWS):
        for c in range(COLS):
            x = c*CELL_SIZE
            y = r*CELL_SIZE
            if (r+c) % 2 == 0:
                ctx.fillStyle = "#fffacd"
            else:
                ctx.fillStyle = "#e6e6fa"
            ctx.fillRect(x,y,CELL_SIZE,CELL_SIZE)

            # nomor
            ctx.fillStyle = "black"
            ctx.font = "12px Arial"
            ctx.fillText(str(num), x+3, y+12)
            num -= 1

    # tangga
    for s,e in ladders.items():
        x1,y1 = cell_center(s)
        x2,y2 = cell_center(e)
        draw_arrow(x1,y1,x2,y2,"green",is_ladder=True)

    # ular
    for s,e in snakes.items():
        x1,y1 = cell_center(s)
        x2,y2 = cell_center(e)
        draw_arrow(x1,y1,x2,y2,"brown",is_ladder=False)

    # pion
    for i,pos in enumerate(player_pos):
        x,y = cell_center(pos)
        offset = (i-1)*10
        ctx.beginPath()
        ctx.arc(x+offset,y,12,0,2*math.pi)
        ctx.fillStyle = players[i]
        ctx.fill()

def roll_animation(player_index):
    rolls = [random.randint(1,6) for _ in range(10)]
    idx = {"val":0}
    def anim():
        if idx["val"] < len(rolls):
            draw_board()
            ctx.fillStyle="black"
            ctx.font="40px Arial"
            ctx.fillText(str(rolls[idx["val"]]), canvas.width//2-10, canvas.height//2)
            idx["val"] += 1
        else:
            timer.clear_interval(tid)
            do_move(player_index, rolls[-1])
    tid = timer.set_interval(anim, 200)

def do_move(player_index, dice):
    global turn, game_over
    if game_over: return
    pos = player_pos[player_index] + dice
    if pos <= 100:
        player_pos[player_index] = pos
        if pos in ladders: player_pos[player_index] = ladders[pos]
        elif pos in snakes: player_pos[player_index] = snakes[pos]
        if player_pos[player_index] == 100:
            info_text.text = f"Pemain {player_index+1} MENANG!"
            game_over=True
    turn = (turn+1) % len(players)
    draw_board()
    if not game_over:
        info_text.text = f"Giliran Pemain {turn+1}"

def roll(ev):
    if not game_over:
        info_text.text = f"Pemain {turn+1} melempar dadu..."
        roll_animation(turn)

def choose_players(ev):
    global players, player_pos
    n = int(ev.target.value)
    colors = ["red","blue","green","orange"]
    players = colors[:n]
    player_pos = [1]*n
    player_select_div.style.display="none"
    roll_button.style.display="inline-block"
    info_text.text = "Giliran Pemain 1"
    draw_board()

for btn in document.select(".player-btn"):
    btn.bind("click", choose_players)

roll_button.bind("click", roll)

draw_board()
