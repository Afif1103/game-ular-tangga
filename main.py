<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Game Ular Tangga - Brython</title>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@3.9.5/brython.min.js"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@3.9.5/brython_stdlib.js"></script>
  <style>
    body { text-align: center; font-family: Arial; }
    #game-canvas { border: 2px solid black; background: #f9f9f9; }
    #controls { margin-top: 10px; }
  </style>
</head>
<body onload="brython()">

<h2>🎲 Game Ular Tangga</h2>

<canvas id="game-canvas" width="600" height="600"></canvas>

<div id="controls">
  <label for="player-count">Jumlah Pemain:</label>
  <select id="player-count">
    <option value="2">2</option>
    <option value="3">3</option>
    <option value="4">4</option>
  </select>
  <button id="start-button">Mulai Game</button>
  <button id="roll-button" disabled>Lempar Dadu</button>
</div>

<script type="text/python">
from browser import document, html, timer
import random, math

# Konstanta
ROWS, COLS = 10, 10
CELL_SIZE = 60
WIDTH, HEIGHT = 600, 600
snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

players = []
current_player = 0
game_started = False
dice_anim_timer = None

colors = ["red", "blue", "green", "purple"]

# --- Fungsi Utility ---
def get_position_coords(pos):
    if pos < 1: pos = 1
    if pos > 100: pos = 100
    row = (pos - 1) // 10
    col = (pos - 1) % 10
    if row % 2 == 1:
        col = 9 - col
    x = col * CELL_SIZE + CELL_SIZE//2
    y = HEIGHT - (row * CELL_SIZE + CELL_SIZE//2)
    return x, y

def draw_board():
    ctx.clearRect(0, 0, WIDTH, HEIGHT)
    # Kotak papan
    for r in range(ROWS):
        for c in range(COLS):
            num = r*10 + c + 1
            if r % 2 == 1:
                num = r*10 + (9-c) + 1
            x = c * CELL_SIZE
            y = HEIGHT - (r+1)*CELL_SIZE
            ctx.fillStyle = "#ffffff" if (r+c)%2==0 else "#ddd"
            ctx.fillRect(x, y, CELL_SIZE, CELL_SIZE)
            ctx.strokeStyle = "black"
            ctx.strokeRect(x, y, CELL_SIZE, CELL_SIZE)
            ctx.fillStyle = "black"
            ctx.font = "12px Arial"
            ctx.fillText(str(num), x+2, y+12)

    # Tangga
    for start, end in ladders.items():
        x1,y1 = get_position_coords(start)
        x2,y2 = get_position_coords(end)
        ctx.strokeStyle = "green"
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
        # panah ke atas
        ctx.beginPath()
        ctx.moveTo(x2, y2)
        ctx.lineTo(x2-5, y2+10)
        ctx.lineTo(x2+5, y2+10)
        ctx.closePath()
        ctx.fillStyle = "green"
        ctx.fill()

    # Ular
    for start, end in snakes.items():
        x1,y1 = get_position_coords(start)
        x2,y2 = get_position_coords(end)
        ctx.strokeStyle = "red"
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
        # panah ke bawah
        ctx.beginPath()
        ctx.moveTo(x2, y2)
        ctx.lineTo(x2-5, y2-10)
        ctx.lineTo(x2+5, y2-10)
        ctx.closePath()
        ctx.fillStyle = "red"
        ctx.fill()

    # Pion
    for i, p in enumerate(players):
        x,y = get_position_coords(p)
        ctx.beginPath()
        ctx.arc(x+(i*10)-10, y, 10, 0, 2*math.pi)
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

# --- Game Flow ---
def start_game(ev):
    global players, current_player, game_started
    n = int(document["player-count"].value)
    players = [0]*n
    current_player = 0
    game_started = True
    document["roll-button"].disabled = False
    draw_board()
    draw_dice(1)

def move_piece(steps):
    global current_player
    def step_move():
        nonlocal steps
        if steps > 0:
            players[current_player] += 1
            draw_board()
            steps -= 1
        else:
            timer.clear_interval(move_timer)
            pos = players[current_player]
            if pos in ladders:
                players[current_player] = ladders[pos]
            elif pos in snakes:
                players[current_player] = snakes[pos]
            draw_board()
            if players[current_player] >= 100:
                ctx.fillStyle = "black"
                ctx.font = "30px Arial"
                ctx.fillText(f"Pemain {current_player+1} Menang!", 150, 300)
                document["roll-button"].disabled = True
            else:
                current_player = (current_player+1)%len(players)
                document["roll-button"].disabled = False
    move_timer = timer.set_interval(step_move, 300)

def animate_dice(ev):
    global dice_anim_timer
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

    dice_anim_timer = timer.set_interval(update, 100)

document["start-button"].bind("click", start_game)
document["roll-button"].bind("click", animate_dice)

draw_board()
draw_dice(1)
</script>

</body>
</html>
