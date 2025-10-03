# block_blast_small_rowclear.py
# Block Blast 8x8 căn giữa, nhỏ gọn, có điểm cao nhất và điểm hiện tại
# ĐÃ FIX: chữ không bị che, block đang kéo luôn hiện trên cùng
# CHỈ XÓA HÀNG, KHÔNG XÓA CỘT

import pygame, random, sys, os

# =========================
# Cấu hình
# =========================
LUOI_KICH_THUOC = 8
O_KICH_THUOC = 50   # nhỏ hơn để màn hình gọn
KHE_O = 4
LE_TREN = 30
MAU_NEN = (20, 24, 28)
MAU_LUOI = (34, 39, 46)
MAU_O_TRONG = (48, 55, 66)
MAU_BONG = (120, 220, 160)
MAU_CHU = (230, 235, 243)
MAU_DO_XAU = (220, 80, 80)
MAU_NEN = (20, 24, 28)
FPS = 60

HIGHSCORE_FILE = "highscore.txt"

# =========================
# Hình dạng khối (không xoay)
# =========================
HINH_DANGS = [
    [(0,0)],
    [(0,0),(1,0)], [(0,0),(0,1)],
    [(0,0),(1,0),(2,0)], [(0,0),(0,1),(0,2)],
    [(0,0),(1,0),(2,0),(3,0)], [(0,0),(0,1),(0,2),(0,3)],
    [(0,0),(1,0),(0,1),(1,1)],             # vuông 2x2
    [(0,0),(0,1),(1,0)],                   # L 3
    [(0,0),(0,1),(0,2),(1,0)],             # L 4
    [(0,0),(1,0),(2,0),(2,1)],             # J 4
    [(0,0),(1,0),(2,0),(1,1)],             # T
    [(0,0),(1,0),(1,1)], [(0,1),(1,1),(1,0)],  # zig
    [(0,0),(1,0),(2,0),(0,1),(1,1)],       # 5 ô
]

PALETTE = [
    (255, 169, 64),
    (123, 201, 82),
    (255, 99, 132),
    (94, 129, 244),
    (255, 206, 86),
    (82, 196, 211),
    (199, 146, 234),
]

# =========================
# Hàm hỗ trợ
# =========================
def kich_thuoc_hinh(shape):
    maxx = max(x for x,_ in shape)
    maxy = max(y for _,y in shape)
    return maxx+1, maxy+1

def hcn_luoi(man_rong):
    w = LUOI_KICH_THUOC*O_KICH_THUOC + (LUOI_KICH_THUOC-1)*KHE_O
    h = LUOI_KICH_THUOC*O_KICH_THUOC + (LUOI_KICH_THUOC-1)*KHE_O
    x = (man_rong - w)//2
    y = LE_TREN + 60
    return pygame.Rect(x, y, w, h)
def ve_gradient(man_hinh, mau_tren, mau_duoi):
    h = man_hinh.get_height()
    w = man_hinh.get_width()
    for y in range(h):
        ti_le = y / h
        r = int(mau_tren[0] * (1 - ti_le) + mau_duoi[0] * ti_le)
        g = int(mau_tren[1] * (1 - ti_le) + mau_duoi[1] * ti_le)
        b = int(mau_tren[2] * (1 - ti_le) + mau_duoi[2] * ti_le)
        pygame.draw.line(man_hinh, (r, g, b), (0, y), (w, y))

def pixel_thanh_o(px, py, gr):
    if not gr.collidepoint(px, py):
        return None
    x = px - gr.x
    y = py - gr.y
    buoc = O_KICH_THUOC + KHE_O
    cx = x // buoc
    cy = y // buoc
    if (x % buoc) >= O_KICH_THUOC or (y % buoc) >= O_KICH_THUOC:
        return None
    if 0 <= cx < LUOI_KICH_THUOC and 0 <= cy < LUOI_KICH_THUOC:
        return int(cx), int(cy)
    return None

def co_the_dat(ban_co, shape, goc):
    ox, oy = goc
    for (sx, sy) in shape:
        x, y = ox + sx, oy + sy
        if not (0 <= x < LUOI_KICH_THUOC and 0 <= y < LUOI_KICH_THUOC):
            return False
        if ban_co[y][x] != 0:
            return False
    return True

def dat_mieng(ban_co, shape, goc, chi_so_mau):
    ox, oy = goc
    for (sx, sy) in shape:
        x, y = ox + sx, oy + sy
        ban_co[y][x] = chi_so_mau + 1

def dong_day(ban_co):
    return [r for r in range(LUOI_KICH_THUOC) if all(ban_co[r][c] != 0 for c in range(LUOI_KICH_THUOC))]

def xoa_dong(ban_co, dongs):
    dem = 0
    for r in dongs:
        for c in range(LUOI_KICH_THUOC):
            ban_co[r][c] = 0
            dem += 1
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
# Lớp Miếng Ghép
# =========================
class MiengGhep:
    def __init__(self, shape, mau):
        self.shape = shape[:]
        self.mau = mau
        self.dang_keo = False
        self.offset = (0,0)
        sx, sy = kich_thuoc_hinh(self.shape)
        self.rong = sx*O_KICH_THUOC + (sx-1)*KHE_O
        self.cao  = sy*O_KICH_THUOC + (sy-1)*KHE_O
        self.vitri = (0,0)

    def hcn(self):
        x, y = self.vitri
        return pygame.Rect(x, y, self.rong, self.cao)

    def ve(self, man_hinh, alpha=255):
        x0, y0 = self.vitri
        s = pygame.Surface((self.rong, self.cao), pygame.SRCALPHA)
        for (sx, sy) in self.shape:
            rx = sx*(O_KICH_THUOC + KHE_O)
            ry = sy*(O_KICH_THUOC + KHE_O)
            pygame.draw.rect(
                s, self.mau + (alpha,),
                pygame.Rect(rx, ry, O_KICH_THUOC, O_KICH_THUOC),
                border_radius=8
            )
        man_hinh.blit(s, (x0, y0))

# =========================
# Tạo bộ bài
# =========================
def tao_mieng():
    return MiengGhep(random.choice(HINH_DANGS), random.choice(PALETTE))

def tao_bo_bai():
    return [ {"piece": tao_mieng(), "used": False} for _ in range(3) ]

def sap_xep_tren_hud(bo_bai, man_rong, gr):
    cach = 40
    tong_rong = sum(slot["piece"].rong for slot in bo_bai) + cach*(len(bo_bai)-1)
    bat_dau_x = (man_rong - tong_rong) // 2
    y = gr.bottom + 40
    x = bat_dau_x
    for slot in bo_bai:
        p = slot["piece"]
        p.vitri = (x, y)
        x += p.rong + cach

# =========================
# Vẽ bàn cờ & chữ
# =========================
def ve_ban_co(man_hinh, ban_co, gr):
    pygame.draw.rect(man_hinh, MAU_LUOI, gr, border_radius=12)
    for r in range(LUOI_KICH_THUOC):
        for c in range(LUOI_KICH_THUOC):
            px = gr.x + c*(O_KICH_THUOC + KHE_O)
            py = gr.y + r*(O_KICH_THUOC + KHE_O)
            o = pygame.Rect(px, py, O_KICH_THUOC, O_KICH_THUOC)
            val = ban_co[r][c]
            if val == 0:
                pygame.draw.rect(man_hinh, MAU_O_TRONG, o, border_radius=8)
            else:
                mau = PALETTE[(val-1) % len(PALETTE)]
                pygame.draw.rect(man_hinh, mau, o, border_radius=8)

def ve_chu(man_hinh, font, text, x, y, mau=MAU_CHU, can_giua=False):
    surf = font.render(text, True, mau)
    rect = surf.get_rect()
    rect.center = (x,y) if can_giua else rect.move(x,y).topleft
    man_hinh.blit(surf, rect)

# =========================
# High Score
# =========================
def doc_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE,"r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def luu_highscore(diem):
    with open(HIGHSCORE_FILE,"w") as f:
        f.write(str(diem))

# =========================
# Vòng đời chính
# =========================
# =========================
# Vòng đời chính
# =========================
def main():
    pygame.init()
    pygame.display.set_caption("Block Blast 8x8 - Small Screen")
    font = pygame.font.SysFont("consolas", 20)
    font_lon = pygame.font.SysFont("consolas", 28, bold=True)

    MAN_RONG, MAN_CAO = 900, 780
    man_hinh = pygame.display.set_mode((MAN_RONG, MAN_CAO))
    dong_ho = pygame.time.Clock()

    def khoi_tao():
        return [[0]*LUOI_KICH_THUOC for _ in range(LUOI_KICH_THUOC)], 0, tao_bo_bai(), False

    ban_co, diem, bo_bai, het_nuoc_di = khoi_tao()
    highscore = doc_highscore()
    gr = hcn_luoi(MAN_RONG)
    sap_xep_tren_hud(bo_bai, MAN_RONG, gr)

    slot_dang_keo = None
    bong_ghost = []
    man_hinh_gameover = False   # flag màn hình game over

    while True:
        dong_ho.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for sk in pygame.event.get():
            if sk.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if sk.type == pygame.KEYDOWN and sk.key == pygame.K_r:
                ban_co, diem, bo_bai, het_nuoc_di = khoi_tao()
                sap_xep_tren_hud(bo_bai, MAN_RONG, gr)
                slot_dang_keo = None
                bong_ghost = []
                man_hinh_gameover = False

            if man_hinh_gameover:
                continue  # bỏ qua input nếu đang ở màn hình Game Over

            if het_nuoc_di: 
                man_hinh_gameover = True
                continue

            # --- xử lý kéo thả ---
            if sk.type == pygame.MOUSEBUTTONDOWN and sk.button == 1:
                for slot in bo_bai:
                    if slot["used"]: continue
                    p = slot["piece"]
                    if p.hcn().collidepoint(mx, my):
                        slot_dang_keo = slot
                        p.dang_keo = True
                        p.offset = (mx - p.vitri[0], my - p.vitri[1])
                        break

            if sk.type == pygame.MOUSEBUTTONUP and sk.button == 1:
                if slot_dang_keo:
                    p = slot_dang_keo["piece"]
                    o = pixel_thanh_o(mx - p.offset[0] + O_KICH_THUOC//2,
                                      my - p.offset[1] + O_KICH_THUOC//2, gr)
                    if o and co_the_dat(ban_co, p.shape, o):
                        chi_so_mau = PALETTE.index(p.mau) % len(PALETTE)
                        dat_mieng(ban_co, p.shape, o, chi_so_mau)
                        diem += len(p.shape)
                        dongs = dong_day(ban_co)
                        so_o_xoa = xoa_dong(ban_co, dongs)
                        if so_o_xoa > 0:
                            diem += so_o_xoa * 2
                            diem += (len(dongs)-1) * 5
                        slot_dang_keo["used"] = True

                        if diem > highscore:
                            highscore = diem
                            luu_highscore(highscore)

                    p.dang_keo = False
                    slot_dang_keo = None
                    bong_ghost = []

                    if all(s["used"] for s in bo_bai):
                        bo_bai = tao_bo_bai()
                        sap_xep_tren_hud(bo_bai, MAN_RONG, gr)

                    if not con_nuoc_di(ban_co, [s for s in bo_bai if not s["used"]]):
                        if all(s["used"] for s in bo_bai):
                            bo_bai = tao_bo_bai()
                            sap_xep_tren_hud(bo_bai, MAN_RONG, gr)
                        if not con_nuoc_di(ban_co, [s for s in bo_bai if not s["used"]]):
                            het_nuoc_di = True
                            man_hinh_gameover = True

            if sk.type == pygame.MOUSEMOTION and slot_dang_keo and slot_dang_keo["piece"].dang_keo:
                p = slot_dang_keo["piece"]
                p.vitri = (mx - p.offset[0], my - p.offset[1])
                bong_ghost = []
                o = pixel_thanh_o(mx - p.offset[0] + O_KICH_THUOC//2,
                                  my - p.offset[1] + O_KICH_THUOC//2, gr)
                if o and co_the_dat(ban_co, p.shape, o):
                    for (sx, sy) in p.shape:
                        bong_ghost.append((o[0]+sx, o[1]+sy))

        # ====================
        # Vẽ màn hình
        # ====================
        ve_gradient(man_hinh, (15, 32, 39), (44, 83, 100))  # xanh đen → xanh xám

        if man_hinh_gameover:
            cx, cy = man_hinh.get_width()//2, man_hinh.get_height()//2
            ve_chu(man_hinh, font_lon, "GAME OVER", cx, cy-40, MAU_DO_XAU, can_giua=True)
            ve_chu(man_hinh, font_lon, f"Điểm hiện tại: {diem}", cx, cy, MAU_CHU, can_giua=True)
            ve_chu(man_hinh, font, f"Điểm cao nhất: {highscore}", cx, cy+40, MAU_CHU, can_giua=True)
            ve_chu(man_hinh, font, "Nhấn R để chơi lại.", cx, cy+80, MAU_CHU, can_giua=True)
        else:
            # --- góc trái: chữ gọn không bị thừa khoảng trắng ---
            LE_TRAI_CHU = 120  

            ve_chu(man_hinh, font_lon, "BLOCK BLAST 8x8", LE_TRAI_CHU, 20)
            ve_chu(man_hinh, font_lon, f"Điểm: {diem}", LE_TRAI_CHU, 50)
            ve_chu(man_hinh, font, f"Điểm cao nhất: {highscore}", LE_TRAI_CHU, 80)
            ve_chu(man_hinh, font, "Nhấn R để chơi lại.", LE_TRAI_CHU, 110)

            ve_ban_co(man_hinh, ban_co, gr)

            if bong_ghost:
                for (x, y) in bong_ghost:
                    px = gr.x + x*(O_KICH_THUOC + KHE_O)
                    py = gr.y + y*(O_KICH_THUOC + KHE_O)
                    pygame.draw.rect(man_hinh, MAU_BONG,
                                    pygame.Rect(px, py, O_KICH_THUOC, O_KICH_THUOC),
                                    border_radius=8)

            sap_xep_tren_hud(bo_bai, MAN_RONG, gr)
            for slot in bo_bai:
                if slot is slot_dang_keo:
                    continue
                p = slot["piece"]
                alpha = 80 if slot["used"] else 255
                p.ve(man_hinh, alpha=alpha)

            if slot_dang_keo:
                slot_dang_keo["piece"].ve(man_hinh)

        pygame.display.flip()

if __name__ == "__main__":
    main()
