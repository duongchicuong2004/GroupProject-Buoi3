

import pygame, random, sys, json, os

def ve_gradient(man_hinh, mau_tren, mau_duoi):
    h = man_hinh.get_height()
    w = man_hinh.get_width()
    for y in range(h):
        ti_le = y / h
        r = int(mau_tren[0] * (1 - ti_le) + mau_duoi[0] * ti_le)
        g = int(mau_tren[1] * (1 - ti_le) + mau_duoi[1] * ti_le)
        b = int(mau_tren[2] * (1 - ti_le) + mau_duoi[2] * ti_le)
        pygame.draw.line(man_hinh, (r, g, b), (0, y), (w, y))

# =========================
# Cau hinh
# =========================
LUOI_KICH_THUOC = 8
O_KICH_THUOC = 42   # <-- giảm kích thước ô để lưới nhỏ hơn
KHE_O = 4
LE_MAN_HINH = 20
HUD_CAO = 200
HUD_SCALE = 0.80
MAU_NEN = (20, 24, 28)
MAU_LUOI = (34, 39, 46)
MAU_VIEN_LUOI = (64, 72, 84)
DO_DAY_VIEN = 6
MAU_O_TRONG = (48, 55, 66)
MAU_BONG = (120, 220, 160)
MAU_CHU = (230, 235, 243)
MAU_DO_XAU = (220, 80, 80)
MAU_VANG = (255, 206, 86)
FPS = 60
HS_FILE = "highscore.json"

HINH_DANGS = [
    [(0,0)],
    [(0,0),(1,0)], [(0,0),(0,1)],
    [(0,0),(1,0),(2,0)], [(0,0),(0,1),(0,2)],
    [(0,0),(1,0),(2,0),(3,0)], [(0,0),(0,1),(0,2),(0,3)],
    [(0,0),(1,0),(0,1),(1,1)],
    [(0,0),(0,1),(1,0)],
    [(0,0),(0,1),(0,2),(1,0)], [(0,0),(1,0),(2,0),(2,1)],
    [(0,0),(1,0),(2,0),(1,1)],
    [(0,0),(1,0),(1,1)], [(0,1),(1,1),(1,0)],
    [(0,0),(1,0),(0,1),(1,1),(2,1)],
    [(0,0),(1,0),(2,0),(0,1),(1,1)],
]

PALETTE = [
    (255, 169, 64),
    (123, 201, 82),
    (255, 99, 132),
    (94, 129, 244),
    (82, 196, 211),
    (199, 146, 234),
    (255, 150, 72),
]

# =========================
# High score helpers
# =========================
def load_high_score():
    try:
        if os.path.exists(HS_FILE):
            with open(HS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", 0))
    except Exception:
        pass
    return 0

def save_high_score(score):
    try:
        with open(HS_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": int(score)}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# =========================
# Tien ich
# =========================
def kich_thuoc_hinh(shape):
    mx = max(x for x,_ in shape)
    my = max(y for _,y in shape)
    return mx+1, my+1

def kich_thuoc_luoi_px():
    w = LUOI_KICH_THUOC*O_KICH_THUOC + (LUOI_KICH_THUOC-1)*KHE_O
    h = LUOI_KICH_THUOC*O_KICH_THUOC + (LUOI_KICH_THUOC-1)*KHE_O
    return w, h

def hcn_luoi_can_giua(screen_w, screen_h):
    grid_w, grid_h = kich_thuoc_luoi_px()
    top_area_h = screen_h - HUD_CAO - LE_MAN_HINH
    top_y = max(LE_MAN_HINH, (top_area_h - grid_h)//2)
    left_x = (screen_w - grid_w)//2
    return pygame.Rect(left_x, top_y, grid_w, grid_h)

def pixel_thanh_o(px, py, gr):
    if not gr.collidepoint(px, py): return None
    x = px - gr.x; y = py - gr.y
    buoc = O_KICH_THUOC + KHE_O
    cx = x // buoc; cy = y // buoc
    if (x % buoc) >= O_KICH_THUOC or (y % buoc) >= O_KICH_THUOC: return None
    cx = int(cx); cy = int(cy)
    if 0 <= cx < LUOI_KICH_THUOC and 0 <= cy < LUOI_KICH_THUOC: return cx, cy
    return None

def co_the_dat(ban_co, shape, goc):
    ox, oy = goc
    for (sx, sy) in shape:
        x, y = ox + sx, oy + sy
        if not (0 <= x < LUOI_KICH_THUOC and 0 <= y < LUOI_KICH_THUOC): return False
        if ban_co[y][x] != 0: return False
    return True

def dat_mieng(ban_co, shape, goc, chi_so_mau):
    ox, oy = goc
    for (sx, sy) in shape:
        x, y = ox + sx, oy + sy
        ban_co[y][x] = chi_so_mau + 1

def dong_cot_day(ban_co):
    rows = [r for r in range(LUOI_KICH_THUOC) if all(ban_co[r][c] != 0 for c in range(LUOI_KICH_THUOC))]
    cols = [c for c in range(LUOI_KICH_THUOC) if all(ban_co[r][c] != 0 for r in range(LUOI_KICH_THUOC))]
    return rows, cols

def xoa_dong_cot(ban_co, rows, cols):
    dem = 0
    for r in rows:
        for c in range(LUOI_KICH_THUOC):
            ban_co[r][c] = 0; dem += 1
    for c in cols:
        for r in range(LUOI_KICH_THUOC):
            ban_co[r][c] = 0; dem += 1
    return dem

def con_nuoc_di(ban_co, slots):
    for slot in slots:
        p = slot["piece"]
        for y in range(LUOI_KICH_THUOC):
            for x in range(LUOI_KICH_THUOC):
                if co_the_dat(ban_co, p.shape, (x,y)):
                    return True
    return False

# =========================
# Lop MiengGhep (co 2 che do: HUD scale & FULL size)
# =========================
class MiengGhep:
    def __init__(self, shape, mau):
        self.shape = shape[:]
        self.mau = mau
        self.dang_keo = False
        self.offset_full = (0,0)
        sx, sy = kich_thuoc_hinh(self.shape)
        self.rong_full = sx*O_KICH_THUOC + (sx-1)*KHE_O
        self.cao_full  = sy*O_KICH_THUOC + (sy-1)*KHE_O
        self.rong_hud = int(self.rong_full * HUD_SCALE)
        self.cao_hud  = int(self.cao_full * HUD_SCALE)
        self.vitri = (0,0)
        self.vitri_mac_dinh = (0,0)
        self.che_do_full = False

    def current_rect(self):
        x,y = self.vitri
        if self.che_do_full:
            return pygame.Rect(x, y, self.rong_full, self.cao_full)
        return pygame.Rect(x, y, self.rong_hud, self.cao_hud)

    def ve(self, man_hinh, alpha=255):
        x0, y0 = self.vitri
        if self.che_do_full:
            s = pygame.Surface((self.rong_full, self.cao_full), pygame.SRCALPHA)
            size = O_KICH_THUOC; gap = KHE_O
        else:
            s = pygame.Surface((self.rong_hud, self.cao_hud), pygame.SRCALPHA)
            size = int(O_KICH_THUOC * HUD_SCALE)
            gap  = int(KHE_O * HUD_SCALE)
        for (sx, sy) in self.shape:
            rx = sx*(size + gap); ry = sy*(size + gap)
            pygame.draw.rect(s, self.mau + (alpha,), pygame.Rect(rx, ry, size, size), border_radius=8)
        man_hinh.blit(s, (x0, y0))

# =========================
# Bo bai & HUD layout
# =========================
def tao_mieng():
    return MiengGhep(random.choice(HINH_DANGS), random.choice(PALETTE))

def tao_bo_bai():
    return [ {"piece": tao_mieng(), "used": False} for _ in range(3) ]

def sap_xep_tren_hud(bo_bai, screen_w, gr):
    spacing_min, spacing_max = 28, 64
    total_pieces_w = sum(slot["piece"].rong_hud for slot in bo_bai)
    n = len(bo_bai)
    hud_left, hud_right = LE_MAN_HINH, screen_w - LE_MAN_HINH
    hud_w = hud_right - hud_left
    spacing_between = (hud_w - total_pieces_w) // max(1, (n + 1))
    spacing_between = max(spacing_min, min(spacing_max, spacing_between))
    total_block = total_pieces_w + spacing_between * (n - 1)
    start_x = hud_left + (hud_w - total_block) // 2
    y = gr.bottom + max(12, (HUD_CAO - max(slot["piece"].cao_hud for slot in bo_bai)) // 2)

    x = start_x
    for slot in bo_bai:
        p = slot["piece"]
        if not p.dang_keo:
            p.che_do_full = False
            p.vitri = (x, y)
            p.vitri_mac_dinh = (x, y)
        x += p.rong_hud + spacing_between

# =========================
# Ve luoi + vien + ban co
# =========================
def ve_luoi_trong(man_hinh, gr):
    vien = gr.inflate(DO_DAY_VIEN*2, DO_DAY_VIEN*2)
    pygame.draw.rect(man_hinh, MAU_VIEN_LUOI, vien, border_radius=14)
    pygame.draw.rect(man_hinh, MAU_LUOI, gr, border_radius=12)
    for r in range(LUOI_KICH_THUOC):
        for c in range(LUOI_KICH_THUOC):
            px = gr.x + c*(O_KICH_THUOC + KHE_O)
            py = gr.y + r*(O_KICH_THUOC + KHE_O)
            pygame.draw.rect(man_hinh, MAU_O_TRONG, pygame.Rect(px, py, O_KICH_THUOC, O_KICH_THUOC), border_radius=8)

def ve_o_da_to(man_hinh, ban_co, gr):
    for r in range(LUOI_KICH_THUOC):
        for c in range(LUOI_KICH_THUOC):
            val = ban_co[r][c]
            if val:
                px = gr.x + c*(O_KICH_THUOC + KHE_O)
                py = gr.y + r*(O_KICH_THUOC + KHE_O)
                pygame.draw.rect(man_hinh, PALETTE[(val-1)%len(PALETTE)], pygame.Rect(px, py, O_KICH_THUOC, O_KICH_THUOC), border_radius=8)

def ve_chu(man_hinh, font, text, x, y, mau=MAU_CHU, can_giua=False):
    surf = font.render(text, True, mau)
    rect = surf.get_rect()
    rect.center = (x,y) if can_giua else rect.move(x,y).topleft
    man_hinh.blit(surf, rect)

# =========================
# Man hinh GAME OVER
# =========================
def render_game_over(man_hinh, screen_w, screen_h, font_big, font, score, high_score):
    man_hinh.fill(MAU_NEN)
    title = "GAME OVER"
    ve_chu(man_hinh, font_big, title, screen_w//2, screen_h//2 - 100, MAU_DO_XAU, True)
    ve_chu(man_hinh, font, f"Diem vua choi: {score}", screen_w//2, screen_h//2 - 40, MAU_CHU, True)
    ve_chu(man_hinh, font, f"High Score: {high_score}", screen_w//2, screen_h//2, MAU_VANG, True)
    ve_chu(man_hinh, font, "Nhan Enter hoac R de choi lai", screen_w//2, screen_h//2 + 60, MAU_CHU, True)
    pygame.display.flip()

# =========================
# Game loop
# =========================
def main():
    pygame.init()
    pygame.display.set_caption("Block Blast 8x8 (Tieng Viet)")
    font = pygame.font.SysFont("consolas", 20)
    font_big = pygame.font.SysFont("consolas", 32, bold=True)
    font_hud_title = pygame.font.SysFont("consolas", 28, bold=True)

    grid_w, grid_h = kich_thuoc_luoi_px()
    SCREEN_W = max(grid_w + 2*LE_MAN_HINH, 900)   # <-- tăng chiều rộng tối thiểu
    SCREEN_H = grid_h + HUD_CAO + 2*LE_MAN_HINH
    man_hinh = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    # Trang thai
    STATE = "play"   # "play" | "over"
    high_score = load_high_score()

    # Khoi tao van choi
    gr = hcn_luoi_can_giua(SCREEN_W, SCREEN_H)
    ban_co = [[0]*LUOI_KICH_THUOC for _ in range(LUOI_KICH_THUOC)]
    diem = 0
    bo_bai = tao_bo_bai()
    sap_xep_tren_hud(bo_bai, SCREEN_W, gr)
    slot_keo = None
    bong = []

    def restart():
        nonlocal gr, ban_co, diem, bo_bai, slot_keo, bong, STATE
        gr = hcn_luoi_can_giua(SCREEN_W, SCREEN_H)
        ban_co = [[0]*LUOI_KICH_THUOC for _ in range(LUOI_KICH_THUOC)]
        diem = 0
        bo_bai = tao_bo_bai()
        sap_xep_tren_hud(bo_bai, SCREEN_W, gr)
        slot_keo = None
        bong = []
        STATE = "play"

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ------------- STATE: OVER -------------
            if STATE == "over":
                if ev.type == pygame.KEYDOWN and (ev.key in (pygame.K_RETURN, pygame.K_r)):
                    restart()
                continue  # bo qua cac su kien khac

            # ------------- STATE: PLAY -------------
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                restart()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for slot in bo_bai:
                    if slot["used"]: continue
                    p = slot["piece"]
                    if p.current_rect().collidepoint(mx, my):
                        slot_keo = slot
                        off_scaled = (mx - p.vitri[0], my - p.vitri[1])
                        p.offset_full = (int(off_scaled[0]/HUD_SCALE), int(off_scaled[1]/HUD_SCALE))
                        p.che_do_full = True
                        p.vitri = (mx - p.offset_full[0], my - p.offset_full[1])
                        p.dang_keo = True
                        break

            if ev.type == pygame.MOUSEMOTION and slot_keo and slot_keo["piece"].dang_keo:
                p = slot_keo["piece"]
                p.vitri = (mx - p.offset_full[0], my - p.offset_full[1])
                bong = []
                # khi kéo hiển thị preview: dùng toạ độ trung tâm ô
                cell = pixel_thanh_o(mx - p.offset_full[0] + O_KICH_THUOC//2,
                                     my - p.offset_full[1] + O_KICH_THUOC//2, gr)
                if cell and co_the_dat(ban_co, p.shape, cell):
                    for (sx,sy) in p.shape:
                        bong.append((cell[0]+sx, cell[1]+sy))

            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if slot_keo:
                    p = slot_keo["piece"]
                    cell = pixel_thanh_o(mx - p.offset_full[0] + O_KICH_THUOC//2,
                                         my - p.offset_full[1] + O_KICH_THUOC//2, gr)
                    if cell and co_the_dat(ban_co, p.shape, cell):
                        idx = PALETTE.index(p.mau) % len(PALETTE)
                        dat_mieng(ban_co, p.shape, cell, idx)
                        rows, cols = dong_cot_day(ban_co)
                        diem += len(p.shape)
                        cleared = xoa_dong_cot(ban_co, rows, cols)
                        if cleared:
                            diem += cleared*2 + (len(rows)+len(cols)-1)*5
                        slot_keo["used"] = True

                    p.dang_keo = False
                    p.che_do_full = False
                    p.vitri = p.vitri_mac_dinh
                    slot_keo = None
                    bong = []

                    if all(s["used"] for s in bo_bai):
                        bo_bai = tao_bo_bai()
                        sap_xep_tren_hud(bo_bai, SCREEN_W, gr)

                    # HẾT NƯỚC -> Man hinh GAME OVER
                    if not con_nuoc_di(ban_co, [s for s in bo_bai if not s["used"]]):
                        # thử tạo bộ mới 1 lần (giữ trải nghiệm giống 1 số game)
                        if all(s["used"] for s in bo_bai):
                            bo_bai = tao_bo_bai()
                            sap_xep_tren_hud(bo_bai, SCREEN_W, gr)
                        # nếu vẫn không có nước đi -> over
                        if not con_nuoc_di(ban_co, [s for s in bo_bai if not s["used"]]):
                            # cập nhật high score
                            file_hs = load_high_score()
                            if diem > max(high_score, file_hs):
                                save_high_score(diem)
                                high_score = diem
                            else:
                                high_score = max(high_score, file_hs)
                            STATE = "over"

        # Nếu đang OVER thì vẽ màn hình over và lặp event tiếp
        if STATE == "over":
            render_game_over(man_hinh, SCREEN_W, SCREEN_H, font_big, font, diem, high_score)
            continue

        # Xóa màn hình (gradient)
        ve_gradient(man_hinh, (15, 32, 39), (44, 83, 100))

        # Vẽ lưới và các ô đã đặt
        ve_luoi_trong(man_hinh, gr)
        ve_o_da_to(man_hinh, ban_co, gr)

        # Vẽ bóng (preview khi kéo)
        if bong:
            for (x, y) in bong:
                px = gr.x + x*(O_KICH_THUOC + KHE_O)
                py = gr.y + y*(O_KICH_THUOC + KHE_O)
                pygame.draw.rect(
                    man_hinh, MAU_BONG,
                    pygame.Rect(px, py, O_KICH_THUOC, O_KICH_THUOC),
                    border_radius=8
                )

        # Vẽ 3 mảnh ở HUD
        sap_xep_tren_hud(bo_bai, SCREEN_W, gr)
        for slot in bo_bai:
            p = slot["piece"]
            if not p.dang_keo:
                p.che_do_full = False
            p.ve(man_hinh, alpha=(80 if slot["used"] else 255))

        # =====================
        # Vẽ High Score + Điểm
        # =====================

        # Tính vị trí lưới
        grid_top = gr.y
        grid_center_x = gr.x + (LUOI_KICH_THUOC * (O_KICH_THUOC + KHE_O)) // 2

        # High Score (góc trái trên màn hình)
        text_hs = f"High Score {high_score}"
        surf_hs = font.render(text_hs, True, MAU_VANG)
        rect_hs = surf_hs.get_rect()
        rect_hs.topleft = (LE_MAN_HINH, LE_MAN_HINH)
        man_hinh.blit(surf_hs, rect_hs)

        # Điểm hiện tại (góc phải trên màn hình)
        text_now = f"Score {diem}"
        surf_now = font.render(text_now, True, MAU_CHU)
        rect_now = surf_now.get_rect()
        rect_now.topright = (SCREEN_W - LE_MAN_HINH, LE_MAN_HINH)
        man_hinh.blit(surf_now, rect_now)

        # Điểm lớn (căn giữa phía trên lưới)
        text_diem = str(diem)
        surf_diem = font_big.render(text_diem, True, MAU_CHU)
        rect_diem = surf_diem.get_rect()
        rect_diem.midtop = (grid_center_x, grid_top - 60)  # cách lưới 60px
        man_hinh.blit(surf_diem, rect_diem)

        # Cập nhật màn hình
        pygame.display.flip()

if __name__ == "__main__":
    main()
