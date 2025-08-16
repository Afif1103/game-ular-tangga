from browser import document, html, timer
import random

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")
cell_size = canvas.width // 10

players = []
positions = []
turn = 0
rolling = False
roll_timer = None
roll_count = 0

# ular dan tangga
ladders = {3:22, 5:8, 11:26, 20:29, 27:56, 21:82, 43:77, 50:91, 57:76, 72:92}
snakes  = {17:4, 19:7, 21:9, 27:1, 54:34, 62:18, 64:60, 87:24, 93:73, 95:75, 98:79}

colors = ["red","blue","green","purple"]

def get_coords(pos):
    if pos < 1: return (0,9)
    pos -= 1
    row = pos // 10
    col = pos % 10
    if row % 2 == 0:
        x = col
    else:
        x = 9 - col
    y = 9 - row
    return (x, y)

def draw_board():
    ctx.clearRect(0,0,canvas.width,canvas.height)
    ctx.font = "14px Arial"
    for i in range(100):
        row = i // 10
        col = i % 10
        if row % 2 == 0:
            x = col
        else:
            x = 9 - col
        y = 9 - row
        ctx.strokeStyle = "black"
        ctx.strokeRect(x*cell_size, y*cell_size, cell_size, cell_size)
        ctx.fillStyle = "black"
        ctx.fillText(str(i+1), x*cell_size+5, y*cell_size+15)
    # tangga
    ctx.strokeStyle = "green"
    ctx.lineWidth = 4
    for s,e in ladders.items():
        x1,y1 = get_coords(s)
        x2,y2 = get_coords(e)
        ctx.beginPath()
        ctx.moveTo(x1*cell_size+cell_size//2, y1*cell_size+cell_size//2)
        ctx.lineTo(x2*cell_size+cell_size//2, y2*cell_size+cell_size//2)
        ctx.stroke()
        ctx.beginPath()
        ctx.moveTo(x2*cell_size+cell_size//2, y2*cell_size+cell_size//2)
        ctx.lineTo(x2*cell_size+cell_size//2-10, y2*cell_size+cell_size//2-10)
        ctx.lineTo(x2*cell_size+cell_size//2+10, y2*cell_size+cell_size//2-10)
        ctx.closePath()
        ctx.fillStyle = "green"
        ctx.fill()
    # ular
    ctx.strokeStyle = "brown"
    ctx.lineWidth = 4
    for s,e in snakes.items():
        x1,y1 = get_coords(s)
        x2,y2 = get_coords(e)
        ctx.beginPath()
        ctx.moveTo(x1*cell_size+cell_size//2, y1*cell_size+cell_size//2)
        ctx.lineTo(x2*cell_size+cell_size//2, y2*cell_size+cell_size//2)
        ctx.stroke()
        ctx.beginPath()
        ctx.moveTo(x2*cell_size+cell_size//2, y2*cell_size+cell_size//2)
        ctx.lineTo(x2*cell_size+cell_size//2-10, y2*cell_size+cell_size//2+10)
        ctx.lineTo(x2*cell_size+cell_size//2+10, y2*cell_size+cell_size//2+10)
        ctx.closePath()
        ctx.fillStyle = "brown"
        ctx.fill()

def draw_players():
    for i,pos in enumerate(positions):
        x,y = get_coords(pos)
        ctx.beginPath()
        ctx.arc(x*cell_size+cell_size//2 + (i*10-15), y*cell_size+cell_size//2, 10, 0, 6.28)
        ctx.fillStyle = colors[i]
        ctx.fill()

def draw_dice(value):
    size = 80
    x, y = canvas.width - size - 10, 10
    ctx.fillStyle = "white"
    ctx.fillRect(x, y, size, size)
    ctx.strokeStyle = "black"
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, size, size)

    ctx.fillStyle = "black"
    r = 6
    mid = x + size//2
    top = y + size//4
    bottom = y + 3*size//4
    left = x + size//4
    right = x + 3*size//4

    positions_map = {
        1: [(mid, mid)],
        2: [(left, top), (right, bottom)],
        3: [(left, top), (mid, mid), (right, bottom)],
        4: [(left, top), (right, top), (left, bottom), (right, bottom)],
        5: [(left, top), (right, top), (mid, mid), (left, bottom), (right, bottom)],
        6: [(left, top), (right, top), (left, mid), (right, mid), (left, bottom), (right, bottom)]
    }

    for (cx, cy) in positions_map[value]:
        ctx.beginPath()
        ctx.arc(cx, cy, r, 0, 6.28)
        ctx.fill()

def start_game(n):
    global players, positions, turn
    players = list(range(n))
    positions = [0]*n
    turn = 0
    document["player-select-div"].style.display = "none"
    document["roll-button"].style.display = "inline"
    document["info-text"].text = f"Pemain {turn+1} giliran lempar dadu"
    draw_board()
    draw_players()

def roll_click(ev):
    global rolling, roll_count
    if rolling: return
    rolling = True
    roll_count = 0
    animate_roll()

def animate_roll():
    global roll_count, roll_timer
    roll_count += 1
    val = random.randint(1,6)
    document["info-text"].text = f"Pemain {turn+1} lempar..."
    draw_board()
    draw_players()
    draw_dice(val)
    if roll_count < 15:
        roll_timer = timer.set_timeout(animate_roll, 100)
    else:
        finish_roll(val)

def finish_roll(val):
    global turn, rolling
    document["info-text"].text = f"Pemain {turn+1} dapat {val}"
    newpos = positions[turn] + val
    if newpos <= 100:
        positions[turn] = newpos
    if positions[turn] in ladders: positions[turn] = ladders[positions[turn]]
    if positions[turn] in snakes: positions[turn] = snakes[positions[turn]]
    draw_board()
    draw_players()
    draw_dice(val)
    if positions[turn] == 100:
        document["info-text"].text = f"🎉 Pemain {turn+1} MENANG!"
        document["roll-button"].style.display = "none"
        return
    turn = (turn+1)%len(players)
    rolling = False
    timer.set_timeout(lambda: document.__setitem__("info-text", f"Pemain {turn+1} giliran lempar dadu"), 1000)

for btn in document.select(".player-btn"):
    btn.bind("click", lambda ev, n=int(ev.target.value): start_game(n))

document["roll-button"].bind("click", roll_click)
