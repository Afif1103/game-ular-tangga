# main.py (Brython)
from browser import document, timer, html
import random, math

# Canvas & context
canvas = document["game-canvas"]
ctx = canvas.getContext("2d")

# Board config
ROWS, COLS = 10, 10
CELL = canvas.width // COLS

# Example snakes & ladders (adjustable)
ladders = {3: 22, 5: 8, 11: 26, 20: 29, 27: 56, 21: 82}   # upward
snakes  = {17: 4, 19: 7, 54: 34, 62: 18, 64: 60, 98: 79}  # downward

# Game state
players = []          # list of color strings for players
positions = []        # numeric positions per player (1..100)
turn = 0
game_over = False

# UI elements
info_text = document["info-text"]
roll_button = document["roll-button"]
player_select_div = document["player-select-div"]

# Colors for up to 4 players
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]  # blue, orange, green, purple

# ---------- Utilities ----------
def cell_center(n):
    """Return (x,y) center pixel of cell number n (1..100) with 1 at left-bottom."""
    if n < 1: n = 1
    if n > 100: n = 100
    row = (n - 1) // COLS               # 0-based from bottom
    col = (n - 1) % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    x = col * CELL + CELL // 2
    y = (ROWS - 1 - row) * CELL + CELL // 2
    return x, y

# ---------- Drawing ----------
def draw_board():
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    # draw cells and numbers (1 bottom-left to 100 top-right)
    num = 1
    for r in range(ROWS):
        for c in range(COLS):
            # compute visual col/row mapping so numbering increases left->right bottom->top zigzag
            row_visual = ROWS - 1 - r
            if row_visual % 2 == 0:
                col_visual = c
            else:
                col_visual = COLS - 1 - c
            x = col_visual * CELL
            y = r * CELL
            # background color
            ctx.fillStyle = "#fffacd" if (r + c) % 2 == 0 else "#e6e6fa"
            ctx.fillRect(x, y, CELL, CELL)
            # border and number
            ctx.strokeStyle = "#333"
            ctx.strokeRect(x, y, CELL, CELL)
            ctx.fillStyle = "#111"
            ctx.font = "12px Arial"
            ctx.fillText(str(num), x + 4, y + 12)
            num += 1

    # draw ladders (green) with arrow pointing up
    ctx.lineWidth = 4
    for s, e in ladders.items():
        x1, y1 = cell_center(s)
        x2, y2 = cell_center(e)
        ctx.strokeStyle = "green"
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
        draw_arrow(x1, y1, x2, y2, "green", is_ladder=True)

    # draw snakes (red) with arrow pointing down
    ctx.lineWidth = 4
    for s, e in snakes.items():
        x1, y1 = cell_center(s)
        x2, y2 = cell_center(e)
        ctx.strokeStyle = "red"
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()
        draw_arrow(x1, y1, x2, y2, "red", is_ladder=False)

    # draw players
    draw_players()

def draw_arrow(x1, y1, x2, y2, color, is_ladder=True):
    """Draw a neat vertical-ish arrow at the end (up for ladder, down for snake)."""
    # draw main line already done by caller. Draw arrow head oriented vertically
    ctx.fillStyle = color
    size = 12
    # For ladder always point slightly upward; for snake point downward
    if is_ladder:
        # arrow pointing up: tip slightly above end point
        tip_x, tip_y = x2, y2 - 1
        angle = -math.pi / 2
    else:
        tip_x, tip_y = x2, y2 + 1
        angle = math.pi / 2
    ctx.beginPath()
    ctx.moveTo(tip_x, tip_y)
    ctx.lineTo(tip_x - size * math.cos(angle - math.pi / 6),
               tip_y - size * math.sin(angle - math.pi / 6))
    ctx.lineTo(tip_x - size * math.cos(angle + math.pi / 6),
               tip_y - size * math.sin(angle + math.pi / 6))
    ctx.closePath()
    ctx.fill()

def draw_players():
    # draw tokens on top of board
    if not positions:
        return
    for i, pos in enumerate(positions):
        x, y = cell_center(pos if pos >= 1 else 1)
        # offset tokens so they don't completely overlap
        offsets = [(-10, 0), (10, 0), (-10, 12), (10, 12)]
        ox, oy = offsets[i] if i < len(offsets) else (0, 0)
        ctx.beginPath()
        ctx.arc(x + ox, y + oy, 12, 0, 2 * math.pi)
        ctx.fillStyle = COLORS[i % len(COLORS)]
        ctx.fill()
        # outline
        ctx.strokeStyle = "#222"
        ctx.lineWidth = 2
        ctx.stroke()

# ---------- Dice (dot-face animation) ----------
def draw_dice_face(value):
    size = 60
    x = canvas.width - size - 10
    y = 10
    # background
    ctx.fillStyle = "white"
    ctx.fillRect(x, y, size, size)
    ctx.strokeStyle = "#222"
    ctx.strokeRect(x, y, size, size)
    # dot positions inside the dice box (relative)
    dots = {
        1: [(0.5, 0.5)],
        2: [(0.25, 0.25), (0.75, 0.75)],
        3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
        4: [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
        5: [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],
        6: [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]
    }
    ctx.fillStyle = "#111"
    for rx, ry in dots[value]:
        cx = x + int(rx * size)
        cy = y + int(ry * size)
        ctx.beginPath()
        ctx.arc(cx, cy, 6, 0, 2 * math.pi)
        ctx.fill()

# ---------- Movement animation ----------
move_timer_id = None
def animate_move(player_idx, steps):
    """Animate step-by-step movement (one cell every 220ms)."""
    global move_timer_id

    step_state = {"remaining": steps}

    def step():
        step_state["remaining"] -= 1
        # advance one
        positions[player_idx] += 1
        if positions[player_idx] > 100:
            # bounce back if overshoot: classic rule optional; here clamp to 100
            positions[player_idx] = 100
        draw_board()
        # finished stepping?
        if step_state["remaining"] <= 0:
            # stop timer
            timer.clear_interval(move_timer_id)
            # after stepping, apply snake/ladder jump (no animation for jump)
            pos = positions[player_idx]
            if pos in ladders:
                positions[player_idx] = ladders[pos]
            elif pos in snakes:
                positions[player_idx] = snakes[pos]
            draw_board()
            finish_turn()
    move_timer_id = timer.set_interval(step, 220)

# ---------- Turn handling ----------
dice_anim_id = None
def roll_dice(ev=None):
    """Start dice animation (random dot faces), then finalize with a value and animate move."""
    global dice_anim_id
    if game_over or not players:
        return
    roll_button.disabled = True
    info_text.text = f"Pemain {turn+1} melempar..."
    flicks = {"count": 0}
    total_flicks = 15

    def flick():
        flicks["count"] += 1
        v = random.randint(1, 6)
        draw_board()
        draw_dice_face(v)
        if flicks["count"] >= total_flicks:
            timer.clear_interval(dice_anim_id)
            final = random.randint(1, 6)
            draw_board()
            draw_dice_face(final)
            # start moving animation stepwise
            animate_move(turn, final)

    dice_anim_id = timer.set_interval(flick, 110)

def finish_turn():
    """Called after move and snake/ladder processing."""
    global turn, game_over
    pos = positions[turn]
    # check win
    if pos >= 100:
        info_text.text = f"🎉 Pemain {turn+1} MENANG!"
        roll_button.disabled = True
        game_over = True
        return
    # next player's turn
    turn = (turn + 1) % len(players)
    info_text.text = f"Giliran Pemain {turn+1}"
    roll_button.disabled = False

# ---------- Setup & Handlers ----------
def start_game(n):
    global players, positions, turn, game_over
    players = [COLORS[i] for i in range(n)]
    positions = [1] * n      # start on square 1
    turn = 0
    game_over = False
    player_select_div.style.display = "none"
    roll_button.style.display = "inline-block"
    roll_button.disabled = False
    info_text.text = f"Giliran Pemain 1"
    draw_board()
    draw_dice_face(1)

# bind player select buttons
for btn in document.select(".player-btn"):
    def handler(ev, b=btn):
        n = int(b.attrs["value"])
        start_game(n)
    btn.bind("click", handler)

# bind roll button
roll_button.bind("click", roll_dice)

# initial draw
draw_board()
draw_dice_face(1)
