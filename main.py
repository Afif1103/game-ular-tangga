import pygame
import sys
import random
import math

# Inisialisasi Pygame
pygame.init()

# --- Konstanta Global ---
# Ukuran layar dan papan permainan
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH // COLS

# Definisi Warna (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 60, 60)
GREEN = (60, 200, 60)
BLUE  = (60, 60, 220)
YELLOW= (220, 200, 60)
DARK  = (40, 40, 40)

# Warna untuk setiap pemain
PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]

# Data posisi Ular dan Tangga
# Format: {kotak_awal: kotak_tujuan}
snakes  = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

# --- Setup Jendela dan Font ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ular Tangga 100 Kotak")
font = pygame.font.SysFont(None, 22)
bigfont = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# --- Fungsi Utilitas ---
def get_pos(square):
    """Mengonversi nomor kotak (1-100) menjadi koordinat piksel (x, y) di tengah kotak."""
    if square < 1: square = 1
    if square > 100: square = 100
    square -= 1
    row = square // COLS
    col = square % COLS
    if row % 2 == 1:  # Baris ganjil (1, 3, 5, ...) bergerak dari kanan ke kiri
        col = COLS - 1 - col
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = (ROWS - 1 - row) * CELL_SIZE + CELL_SIZE // 2
    return x, y

def draw_arrowhead(surface, tip, tail, color):
    """Menggambar mata panah di titik 'tip' yang menunjuk dari 'tail'."""
    tx, ty = tip
    sx, sy = tail
    dx, dy = tx - sx, ty - sy
    L = math.hypot(dx, dy)
    if L == 0: return
    ux, uy = dx / L, dy / L
    head_len = 20
    head_w   = 10
    base_x = tx - ux * head_len
    base_y = ty - uy * head_len
    left  = (base_x - uy * head_w, base_y + ux * head_w)
    right = (base_x + uy * head_w, base_y - ux * head_w)
    pygame.draw.polygon(surface, color, [(tx, ty), left, right])

# --- Fungsi Menggambar ---
def draw_board():
    """Menggambar seluruh papan permainan, termasuk nomor, ular, dan tangga."""
    screen.fill(WHITE)
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            draw_row = ROWS - 1 - r
            base = draw_row * COLS
            if draw_row % 2 == 0:
                num = base + c + 1
            else:
                num = base + (COLS - 1 - c) + 1
            pygame.draw.rect(screen, BLACK, rect, 1)
            text = font.render(str(num), True, BLACK)
            screen.blit(text, (rect.x + 4, rect.y + 4))

    for start, end in snakes.items():
        sx, sy = get_pos(start)
        ex, ey = get_pos(end)
        pygame.draw.line(screen, RED, (sx, sy), (ex, ey), 8)
        draw_arrowhead(screen, (ex, ey), (sx, sy), RED)

    for start, end in ladders.items():
        sx, sy = get_pos(start)
        ex, ey = get_pos(end)
        pygame.draw.line(screen, GREEN, (sx, sy), (ex, ey), 8)
        draw_arrowhead(screen, (ex, ey), (sx, sy), GREEN)

def draw_players(positions):
    """Menggambar semua pion pemain di posisi mereka saat ini."""
    offsets = [(0,0), (10,10), (-10,10), (10,-10)]
    for i, sq in enumerate(positions):
        x, y = get_pos(sq)
        ox, oy = offsets[i] if i < len(offsets) else (0, 0)
        pygame.draw.circle(screen, PLAYER_COLORS[i], (x+ox, y+oy), 12)
        pygame.draw.circle(screen, DARK, (x+ox, y+oy), 12, 2)

def draw_dice(surface, value):
    """Menggambar tampilan dadu dengan angka tertentu."""
    surface.fill((255, 255, 255, 230))
    pygame.draw.rect(surface, BLACK, (0, 0, 80, 80), 3, border_radius=8)
    dots = {
        1: [(40, 40)], 2: [(20, 20), (60, 60)], 3: [(20, 20), (40, 40), (60, 60)],
        4: [(20, 20), (60, 20), (20, 60), (60, 60)],
        5: [(20, 20), (60, 20), (40, 40), (20, 60), (60, 60)],
        6: [(20, 20), (60, 20), (20, 40), (60, 40), (20, 60), (60, 60)]
    }
    if value in dots:
        for px, py in dots[value]:
            pygame.draw.circle(surface, BLACK, (px, py), 6)

# --- Fungsi Logika Permainan ---
def roll_dice_animation(current_positions, duration=3.0, interval_ms=250):
    """Menampilkan animasi dadu yang sedang dikocok."""
    dice_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    val = 1
    start_ms = pygame.time.get_ticks()
    last_ms = start_ms - interval_ms

    while pygame.time.get_ticks() - start_ms < int(duration * 1000):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        now = pygame.time.get_ticks()
        if now - last_ms >= interval_ms:
            val = random.randint(1, 6)
            last_ms = now
        draw_board()
        draw_players(current_positions)
        draw_dice(dice_surface, val)
        screen.blit(dice_surface, (WIDTH - 100, 20))
        pygame.display.flip()
        clock.tick(60)
    return random.randint(1, 6)

def move_player_stepwise(positions, player_idx, steps):
    """Menggerakkan pion pemain selangkah demi selangkah."""
    for _ in range(steps):
        if positions[player_idx] >= 100: break
        positions[player_idx] += 1
        draw_board()
        draw_players(positions)
        pygame.display.flip()
        pygame.time.wait(220)
    
    sq = positions[player_idx]
    if sq in snakes:
        positions[player_idx] = snakes[sq]
    elif sq in ladders:
        positions[player_idx] = ladders[sq]
    
    # Setelah turun/naik, gambar ulang posisi akhir
    draw_board()
    draw_players(positions)
    pygame.display.flip()
    pygame.time.wait(300)

# --- Fungsi UI (Antarmuka Pengguna) ---
def draw_button(rect, label, hovered=False):
    """Menggambar tombol yang bisa diklik."""
    color = GREEN if not hovered else (80, 230, 80)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, DARK, rect, 2, border_radius=12)
    text = bigfont.render(label, True, WHITE)
    screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))

def menu_pemain_mouse():
    """Menampilkan menu untuk memilih jumlah pemain."""
    while True:
        screen.fill(WHITE)
        title = bigfont.render("Pilih Jumlah Pemain", True, BLACK)
        subtitle = font.render("Klik salah satu tombol di bawah", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 160))

        buttons = []
        w, h, gap = 120, 60, 20
        total_w = 3*w + 2*gap
        start_x = WIDTH//2 - total_w//2
        y = 240
        for i, val in enumerate((2, 3, 4)):
            rect = pygame.Rect(start_x + i*(w+gap), y, w, h)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            draw_button(rect, str(val), hovered)
            buttons.append((rect, val))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, val in buttons:
                    if rect.collidepoint(event.pos):
                        return val
        clock.tick(60)

# --- Fungsi Utama (Main Loop) ---
def main():
    """Fungsi utama yang menjalankan seluruh alur permainan."""
    num_players = menu_pemain_mouse()
    positions = [1] * num_players
    turn = 0
    winner = None
    dice_result = None  # Variabel untuk "mengingat" hasil dadu terakhir

    dice_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    running = True
    while running:
        # Penanganan Event (Input dari pengguna)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if winner is None and event.key == pygame.K_SPACE:
                    rolled_value = roll_dice_animation(positions)
                    dice_result = rolled_value
                    move_player_stepwise(positions, turn, dice_result)
                    if positions[turn] >= 100:
                        positions[turn] = 100
                        winner = turn
                    if winner is None:
                        turn = (turn + 1) % num_players

        # Logika Menggambar (Apa yang tampil di layar)
        draw_board()
        draw_players(positions)
        if dice_result is not None:
            draw_dice(dice_surface, dice_result)
            screen.blit(dice_surface, (WIDTH - 100, 20))

        if winner is None:
            info_text = f"Giliran Player {turn+1} — Tekan [SPASI] untuk lempar dadu"
        else:
            info_text = f"🎉 Player {winner+1} MENANG! Tekan [ESC] untuk keluar."
        info_surface = font.render(info_text, True, BLACK)
        screen.blit(info_surface, (10, 10))

        # Update Tampilan
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()