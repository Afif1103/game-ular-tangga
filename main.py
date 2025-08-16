from browser import document, html, timer
import random, math

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

ROWS, COLS = 10, 10
CELL_SIZE = canvas.width // COLS

# Papan ular tangga (start=kotak bawah, end=kotak atas)
snakes = {99: 7, 92: 35, 73: 53, 63: 22, 87: 56}
ladders = {3: 51, 6: 27, 20: 70, 36: 55, 63: 95}

players = []
current_player = 0
game_started = False

# 🎨 gambar papan
def draw_board():
    ctx.clearRect(0,0,canvas.width,canvas.height)
    num = 1
    for r in range(ROWS):
        for c in range(COLS):
            row = ROWS - 1 - r
            if row % 2 == 0:
                col = c
            else:
                col = COLS - 1 - c
            x = col * CELL_SIZE
            y = r * CELL_SIZE

            ctx.fillStyle = "#fffacd" if (r+c)%2==0 else "#e6e6fa"
            ctx.fillRect(x,y,CELL_SIZE,CELL_SIZE)

            ctx.strokeStyle="black"
            ctx.strokeRect(x,y,CELL_SIZE,CELL_SIZE)

            ctx.fillStyle="black"
            ctx.font="12px Arial"
            ctx.fillText(str(num), x+3, y+12)
            num += 1

    # gambar tangga
    ctx.strokeStyle="green"
    ctx.lineWidth=5
    for start,end in ladders.items():
        x1,y1 = cell_center(start)
        x2,y2 = cell_center(end)
        ctx.beginPath()
        ctx.moveTo(x1,y1)
        ctx.lineTo(x2,y2)
        ctx.stroke()
        draw_arrow(x1,y1,x2,y2,"green")

    # gambar ular
    ctx.strokeStyle="red"
    ctx.lineWidth=5
    for start,end in snakes.items():
        x1,y1 = cell_center(start)
        x2,y2 = cell_center(end)
        ctx.beginPath()
        ctx.moveTo(x1,y1)
        ctx.lineTo(x2,y2)
        ctx.stroke()
        draw_arrow(x1,y1,x2,y2,"red")

# 🔺 anak panah
def draw_arrow(x1,y1,x2,y2,color):
    ang = math.atan2(y2-y1,x2-x1)
    ctx.fillStyle=color
    ctx.beginPath()
    ctx.moveTo(x2,y2)
    ctx.lineTo(x2-10*math.cos(ang-math.pi/6), y2-10*math.sin(ang-math.pi/6))
    ctx.lineTo(x2-10*math.cos(ang+math.pi/6), y2-10*math.sin(ang+math.pi/6))
    ctx.closePath()
    ctx.fill()

# hitung posisi pion
def cell_center(n):
    row = (n-1)//COLS
    col = (n-1)%COLS
    if row % 2 == 1:
        col = COLS-1-col
    x = col*CELL_SIZE + CELL_SIZE//2
    y = (ROWS-1-row)*CELL_SIZE + CELL_SIZE//2
    return (x,y)

# 🎲 dadu animasi
def roll_dice(ev=None):
    roll_button.disabled = True
    rolls = 15
    def animate(i=0):
        val = random.randint(1,6)
        draw_board()
        draw_players()
        draw_dice(val)
        if i < rolls:
            timer.set_timeout(lambda: animate(i+1), 120)
        else:
            move_player(val)
    animate()

# gambar dadu
def draw_dice(val):
    size=60
    x=canvas.width-size-10
    y=10
    ctx.fillStyle="white"
    ctx.fillRect(x,y,size,size)
    ctx.strokeStyle="black"
    ctx.strokeRect(x,y,size,size)
    ctx.fillStyle="black"
    dots={
        1:[(0.5,0.5)],
        2:[(0.25,0.25),(0.75,0.75)],
        3:[(0.25,0.25),(0.5,0.5),(0.75,0.75)],
        4:[(0.25,0.25),(0.25,0.75),(0.75,0.25),(0.75,0.75)],
        5:[(0.25,0.25),(0.25,0.75),(0.5,0.5),(0.75,0.25),(0.75,0.75)],
        6:[(0.25,0.25),(0.25,0.5),(0.25,0.75),(0.75,0.25),(0.75,0.5),(0.75,0.75)]
    }
    for (dx,dy) in dots[val]:
        ctx.beginPath()
        ctx.arc(x+dx*size,y+dy*size,5,0,2*math.pi)
        ctx.fill()

# gerakan pion
def move_player(val):
    global current_player
    player = players[current_player]
    pos = player["pos"]+val
    if pos>100: pos=100-(pos-100)
    if pos in ladders: pos=ladders[pos]
    if pos in snakes: pos=snakes[pos]
    player["pos"]=pos

    draw_board()
    draw_players()
    draw_dice(val)

    if pos==100:
        document["info-text"].text = f"Pemain {current_player+1} MENANG!"
        roll_button.disabled=True
        return
    current_player=(current_player+1)%len(players)
    document["info-text"].text=f"Giliran Pemain {current_player+1}"
    roll_button.disabled=False

# gambar pion
def draw_players():
    colors=["blue","orange","purple","black"]
    for i,p in enumerate(players):
        x,y=cell_center(p["pos"])
        ctx.beginPath()
        ctx.arc(x+ (i-1.5)*8, y, 10, 0, 2*math.pi)
        ctx.fillStyle=colors[i]
        ctx.fill()

# mulai game
def start_game(num):
    global players, game_started, current_player
    players=[{"pos":1} for _ in range(num)]
    current_player=0
    game_started=True
    document["player-select-div"].style.display="none"
    roll_button.style.display="inline-block"
    document["info-text"].text=f"Giliran Pemain 1"
    draw_board()
    draw_players()

# --- event listener ---
roll_button = document["roll-button"]
roll_button.bind("click",roll_dice)

for btn in document.select(".player-btn"):
    btn.bind("click", lambda ev, b=btn: start_game(int(b.value)))

# awal
draw_board()
