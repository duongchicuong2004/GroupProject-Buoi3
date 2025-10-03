import pygame
import sys
import random

# --- cấu hình ---
WIDTH, HEIGHT = 600, 800
ROWS, COLS = 10, 10
BLOCK_SIZE = 50
GRID_OFFSET_Y = 120

# khởi tạo pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast Clone")
font = pygame.font.SysFont("Arial", 32)

# màu sắc
BLACK = (0, 0, 0)
GRAY = (50, 50, 70)
WHITE = (255, 255, 255)
COLORS = [
    (0, 180, 255), (255, 100, 100), (0, 200, 0),
    (255, 200, 0), (180, 0, 255), (255, 140, 0)
]

# bàn cờ
grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
score = 0

# block mẫu
BLOCK_SHAPES = [
    [[1]], [[1, 1]], [[1], [1]],
    [[1, 1], [1, 1]], [[1, 1, 1]],
    [[1], [1], [1]], [[1, 1, 1, 1]],
    [[1], [1], [1], [1]],
    [[1, 0], [1, 0], [1, 1]],
    [[0, 1], [0, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]]
]

def generate_block():
    shape = random.choice(BLOCK_SHAPES)
    color = random.choice(COLORS)
    return {"shape": shape, "color": color, "pos": [0, 0], "dragging": False}

def can_place(block, row, col):
    shape = block["shape"]
    for r in range(len(shape)):
        for c in range(len(shape[0])):
            if shape[r][c] == 1:
                rr, cc = row + r, col + c
                if rr < 0 or rr >= ROWS or cc < 0 or cc >= COLS:
                    return False
                if grid[rr][cc] is not None:
                    return False
    return True

def place_block(block, row, col):
    shape = block["shape"]
    for r in range(len(shape)):
        for c in range(len(shape[0])):
            if shape[r][c] == 1:
                grid[row + r][col + c] = block["color"]

def clear_full_lines():
    global score
    cleared = 0
    # hàng
    for r in range(ROWS):
        if all(grid[r][c] is not None for c in range(COLS)):
            cleared += 1
            for c in range(COLS):
                grid[r][c] = None
    # cột
    for c in range(COLS):
        if all(grid[r][c] is not None for r in range(ROWS)):
            cleared += 1
            for r in range(ROWS):
                grid[r][c] = None
    score += cleared * 10

def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c*BLOCK_SIZE, GRID_OFFSET_Y+r*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            color = grid[r][c] if grid[r][c] else GRAY
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_block(block, pos=None):
    shape = block["shape"]
    color = block["color"]
    bx, by = pos if pos else block["pos"]
    for r in range(len(shape)):
        for c in range(len(shape[0])):
            if shape[r][c] == 1:
                rect = pygame.Rect(bx + c*BLOCK_SIZE, by + r*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

def any_move_possible(blocks):
    """Kiểm tra xem còn chỗ đặt block nào không"""
    for b in blocks:
        shape = b["shape"]
        for r in range(ROWS):
            for c in range(COLS):
                if can_place(b, r, c):
                    return True
    return False

def main():
    global score
    clock = pygame.time.Clock()

    # 3 block ban đầu
    blocks = [generate_block() for _ in range(3)]
    for i, b in enumerate(blocks):
        b["pos"] = [100 + i*150, 700]

    dragging_block = None
    offset_x, offset_y = 0, 0

    running = True
    while running:
        screen.fill((20, 30, 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for b in blocks:
                    bx, by = b["pos"]
                    bw = len(b["shape"][0]) * BLOCK_SIZE
                    bh = len(b["shape"]) * BLOCK_SIZE
                    if bx <= x <= bx+bw and by <= y <= by+bh:
                        dragging_block = b
                        offset_x = x - bx
                        offset_y = y - by
                        b["dragging"] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_block:
                    x, y = pygame.mouse.get_pos()
                    col = x // BLOCK_SIZE
                    row = (y - GRID_OFFSET_Y) // BLOCK_SIZE
                    if can_place(dragging_block, row, col):
                        place_block(dragging_block, row, col)
                        clear_full_lines()
                        blocks.remove(dragging_block)
                        if not blocks:
                            blocks = [generate_block() for _ in range(3)]
                            for i, b in enumerate(blocks):
                                b["pos"] = [100 + i*150, 700]
                    dragging_block["dragging"] = False
                    dragging_block = None

            elif event.type == pygame.MOUSEMOTION and dragging_block:
                x, y = pygame.mouse.get_pos()
                dragging_block["pos"] = [x - offset_x, y - offset_y]

        # --- vẽ ---
        draw_grid()
        if dragging_block:
            draw_block(dragging_block)
        for b in blocks:
            if not b["dragging"]:
                draw_block(b)

        # điểm
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # kiểm tra game over
        if not any_move_possible(blocks):
            over_text = font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(over_text, (200, 50))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
