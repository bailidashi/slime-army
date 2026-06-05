"""
桌面宠物 — 史莱姆
==========================

"""

import sys, random, math, os, subprocess, time, threading, re
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QSystemTrayIcon, QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QIcon, QFont, QCursor
from PIL import ImageGrab  # 截屏取背景色
import numpy as np  # 钓鱼视觉检测
import pyautogui  # 钓鱼鼠标控制

# ====================================================
#  皮肤系统
# ====================================================
# 全局当前皮肤数据（不是 property，直接当变量用）
IDLE_PX   = []
JUMP_PX   = []
SQUASH_PX = []
SLEEP_PX  = []
PALETTE   = {}
FIXED_KEYS = set()

SKINS = []
SKIN_INDEX = 0

def _auto_jump(px):
    """生成跳跃帧：底部加身体行"""
    if len(px) < 2: return px[:]
    j = px[:]
    mid = px[len(px)//2]
    j.insert(len(j)-1, mid)
    j.insert(len(j)-1, mid)
    return j

def _auto_squash(px):
    """生成压扁帧：裁掉几行"""
    if len(px) <= 5: return px[:]
    keep = max(6, len(px) - 4)
    return px[1:1+keep]

def _auto_sleep(px):
    """生成睡觉帧：中间行眼睛变---"""
    s = [list(row) for row in px[:max(6, len(px)-4)]]
    eye_row = len(s) // 2 - 1
    if 0 <= eye_row < len(s):
        for i in range(eye_row, min(eye_row+2, len(s))):
            row = s[i]
            mid = len(row) // 2
            for j in range(mid-2, mid+2):
                if 0 <= j < len(row):
                    row[j] = '-'
    return [''.join(r) for r in s]

def add_skin(name, idle_px, palette, fixed=None, blend=0.35):
    """注册一个皮肤"""
    SKINS.append({
        "name": name,
        "idle": idle_px,
        "jump": _auto_jump(idle_px),
        "squash": _auto_squash(idle_px),
        "sleep": _auto_sleep(idle_px),
        "palette": palette,
        "fixed": fixed or set(),
        "blend": blend,
        "cols": len(idle_px[0]),
    })

def apply_skin(index):
    """切换到指定皮肤"""
    global SKIN_INDEX, IDLE_PX, JUMP_PX, SQUASH_PX, SLEEP_PX, PALETTE, FIXED_KEYS
    s = SKINS[index]
    SKIN_INDEX = index
    IDLE_PX   = s["idle"]
    JUMP_PX   = s["jump"]
    SQUASH_PX = s["squash"]
    SLEEP_PX  = s["sleep"]
    PALETTE   = s["palette"]
    FIXED_KEYS = s["fixed"]
    Slime.COLS = s["cols"]
    Slime.ROWS = len(IDLE_PX)

# ========== 注册皮肤 ==========
add_skin("紫晶史莱姆", [
    "...........D....",
    "..........DDD...",
    ".....FFFFFFDDD..",
    "...FFIJJHGGGDC..",
    "..FGJKKIJHFGGC..",
    ".FGHJKKIJFHFGFC.",
    ".FHHHJJJHHFHGGC.",
    "FFGHHHHHHHHHGGFC",
    "FGGAHHBBBHAHHGGFC",
    "FEEHHBBBHHHEEGFC",
    "FFGGHHHHHHGGGFFC",
    "CFFGGGGGGGGFFFFC",
    ".CFFFFFFFFFFFFC.",
    "..CCCCCCCCCCCCC.",
], {
    'A': QColor(47, 31, 68), 'B': QColor(51, 28, 74), 'C': QColor(50, 27, 79),
    'D': QColor(128, 40, 40), 'E': QColor(168, 59, 63), 'F': QColor(113, 73, 165),
    'G': QColor(143, 99, 184), 'H': QColor(159, 127, 211), 'I': QColor(214, 176, 224),
    'J': QColor(216, 177, 223), 'K': QColor(244, 212, 226), '-': QColor(80, 60, 100),
}, fixed={'D', 'E'})

add_skin("史莱姆王", [
    "..C.C.C.C...",
    ".CPCICICNC..",
    ".EJPBBBBCNC.",
    ".EENCMPPNCC.",
    ".CMDDDDDDAC.",
    ".DDKHHOOOKG.",
    "FKKHHOLLLOHG",
    "FKKHHOLLLOHG",
    "FKKHHHOOOHHG",
    "FKKKHHHHHHKG",
    ".FFGGGGGGGG.",
], {
    'A': QColor(57, 25, 81), 'B': QColor(56, 25, 85), 'C': QColor(83, 61, 32),
    'D': QColor(0, 59, 130), 'E': QColor(140, 20, 45), 'F': QColor(3, 60, 175),
    'G': QColor(2, 62, 176), 'H': QColor(0, 95, 197), 'I': QColor(161, 134, 56),
    'J': QColor(240, 63, 49), 'K': QColor(74, 78, 204), 'L': QColor(1, 149, 235),
    'M': QColor(254, 202, 1), 'N': QColor(255, 202, 2), 'O': QColor(116, 135, 237),
    'P': QColor(255, 254, 179), '-': QColor(60, 60, 100),
}, fixed={'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'})  # 史莱姆王不变色

add_skin("风史莱姆", [
    "...A.....AAAAA.....A...",
    "..AFA.AAACCCCCAAA.AFA..",
    "..AHFACCCCCCCCCCCAFHA..",
    "..AHFFACCCCCCCCCAFFHA..",
    "..AAHHCCCCCCCCCCCFHAA..",
    ".ACCACCBCCCCCCCBCCACCA.",
    ".ACCCCBHBCCCCCBHBCCCCA.",
    "ACCCCBHIHBCCCBHIHBCCCCA",
    "ACCCCBHIHBCCCBHIHBCCCCA",
    "ACFCFBHIHBGDGBHIHBFCFCA",
    "AFCFCFBHBGDGDGBHBGCFCFA",
    "AFFFFFFBFFFFFFFBFFFFFFA",
    "AFFFFFFFFFFFFFFFFFFFFFA",
    ".AFFFFFFFFFFFFFFFFFFFA.",
    "..AEEEEEEEEEEEEEEFFFA..",
    "...AAAAAAAAAAAAAAAAA...",
], {
    'A': QColor(1, 1, 3), 'B': QColor(60, 152, 210), 'C': QColor(72, 186, 187),
    'D': QColor(72, 188, 186), 'E': QColor(161, 221, 233), 'F': QColor(159, 223, 235),
    'G': QColor(165, 221, 236), 'H': QColor(167, 231, 232), 'I': QColor(255, 255, 255),
    '-': QColor(100, 180, 200),
}, fixed={'A','B','C','D','E','F','G','H','I'})  # 风史莱姆不变色

add_skin("宝宝", [
    "AA..............AA",
    "ADA..AAAAAAA..ADA",
    "AAA.ABBBBBBBA.AAA",
    "...ABBBBBBBBBBA...",
    "..ABBBCBBBCBBBA..",
    "..AEBBCBBBCBEBA..",
    "..AEBBBBBBBBBEA..",
    "..ABBBBBBBBBBBA..",
    "...ABBBBBBBBA....",
    "....AAAAAAAAA....",
], {
    'A': QColor(40, 92, 128), 'B': QColor(168, 209, 236),
    'C': QColor(236, 225, 168), 'D': QColor(212, 232, 245),
    'E': QColor(240, 240, 240), '-': QColor(100, 150, 180),
}, fixed={'A','B','C','D','E'})  # 宝宝不变色

add_skin("MC史莱姆", [
    "BBBBBBBBBBBB",
    "BEEEEEEEEDDB",
    "BECCCCCCEDDB",
    "BEAACCAAEDDB",
    "BEAACCAAEDDB",
    "BECCCCCCEDDB",
    "BECCCACCEDDB",
    "BECCCCCCEDDB",
    "BEEEEEEEEDDB",
    "BBBBBBBBBBBB",
], {
    'A': QColor(8, 1, 4), 'B': QColor(3, 3, 9), 'C': QColor(28, 157, 71),
    'D': QColor(21, 164, 76), 'E': QColor(98, 201, 124), '-': QColor(40, 100, 60),
}, fixed={'A','B','C','D','E'})  # MC史莱姆永远绿色

add_skin("炫彩史莱姆", [
    ".....CCCCC.....",
    "...CCDDDDDCC...",
    "..CDDDDDDDDDC..",
    ".CDDDDDDDDDEDC.",
    "CDDDDDDDDDDDDDC",
    "CDDDDADDDADDEDC",
    "CDDDDBDDDBDDEDC",
    "CDDDDBDDDBDDEDC",
    "CDDDDDDDDDDEDDC",
    ".CCDDDDDDDDDCC.",
    "..CCCCCCCCCC...",
], {
    'A': QColor(2, 0, 1), 'B': QColor(54, 19, 75), 'C': QColor(111, 210, 242),
    'D': QColor(188, 236, 255), 'E': QColor(251, 249, 252), '-': QColor(80, 140, 180),
}, fixed=set(), blend=0.9)  # 炫彩史莱姆：90% 融合背景

# ========== 自定义皮肤（skins 文件夹）==========
CUSTOM_SKINS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skins")
BUILTIN_COUNT = len(SKINS)  # 内置皮肤数量

def _parse_skin_file(filepath):
    """解析皮肤文件，返回 (name, idle_px, palette) 或 None"""
    try:
        with open(filepath, encoding="utf-8") as f:
            code = f.read()
        # 解析 PALETTE
        palette = {}
        for m in re.finditer(r"'(\w+)':\s*QColor\((\d+),\s*(\d+),\s*(\d+)\)", code):
            palette[m.group(1)] = QColor(int(m.group(2)), int(m.group(3)), int(m.group(4)))
        # 解析 SLIME_PX
        px_match = re.search(r'SLIME_PX\s*=\s*\[(.*?)\]', code, re.DOTALL)
        if not px_match or not palette: return None
        rows = re.findall(r'"([^"]*)"', px_match.group(1))
        if not rows: return None
        name = os.path.splitext(os.path.basename(filepath))[0]
        return name, rows, palette
    except:
        return None

def _load_custom_skins():
    """扫描 skins 文件夹，加载所有自定义皮肤"""
    if not os.path.exists(CUSTOM_SKINS_DIR):
        os.makedirs(CUSTOM_SKINS_DIR)
        return
    # 清掉之前加载的自定义（保留内置）
    del SKINS[BUILTIN_COUNT:]
    for fname in sorted(os.listdir(CUSTOM_SKINS_DIR)):
        if not fname.endswith(".py"): continue
        result = _parse_skin_file(os.path.join(CUSTOM_SKINS_DIR, fname))
        if result:
            name, px, pal = result
            add_skin(f"[自] {name}", px, pal, fixed=set(), blend=0.35)

def _save_custom_skin(name, code):
    """保存自定义皮肤到文件"""
    if not os.path.exists(CUSTOM_SKINS_DIR):
        os.makedirs(CUSTOM_SKINS_DIR)
    fname = "".join(c for c in name if c.isalnum() or c in "._- ") or "unnamed"
    path = os.path.join(CUSTOM_SKINS_DIR, fname + ".py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    _load_custom_skins()

def _delete_custom_skin(index):
    """删除自定义皮肤"""
    if index < BUILTIN_COUNT: return
    s = SKINS[index]
    fname = "".join(c for c in s["name"].replace("[自] ", "") if c.isalnum() or c in "._- ") or "unnamed"
    path = os.path.join(CUSTOM_SKINS_DIR, fname + ".py")
    if os.path.exists(path):
        os.remove(path)
    _load_custom_skins()
    apply_skin(0)

class Slime:
    PX_SCALE = 7
    COLS = 15  # apply_skin 会更新
    CANVAS = 160

    @staticmethod
    def make(state: str, frame: int, bg_color: tuple = None) -> QPixmap:
        pix = QPixmap(Slime.CANVAS, Slime.CANVAS + 30)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing, False)

        s = Slime.PX_SCALE
        bw = Slime.COLS * s   # 身体像素宽
        bh = Slime.ROWS * s   # 身体像素高

        # ========== 背景色换色相 ==========
        tint_palette = PALETTE.copy()
        if bg_color:
            br, bg, bb = bg_color
            # 取背景的色相和亮度
            bhue, bsat, blight = Slime._rgb_to_hsl(br, bg, bb)
            # 如果背景太暗，加一点亮度让史莱姆不至于全黑
            if blight < 0.25:
                blight = 0.25

            blend = SKINS[SKIN_INDEX].get("blend", 0.35)
            for key, color in PALETTE.items():
                if key in FIXED_KEYS:
                    tint_palette[key] = color
                    continue
                r, g, b = color.red(), color.green(), color.blue()
                _, sat, light = Slime._rgb_to_hsl(r, g, b)
                if light < 0.15 or sat < 0.1:
                    tint_palette[key] = color
                else:
                    new_light = light * (1 - blend) + blight * blend
                    nr, ng, nb = Slime._hsl_to_rgb(bhue, sat, new_light)
                    tint_palette[key] = QColor(nr, ng, nb)

        # ========== 果冻形变参数 ==========
        sx, sy = 1.0, 1.0       # 缩放
        offset_y = 0             # 垂直偏移
        px = IDLE_PX

        if state == "sleep":
            px = SLEEP_PX
            sx, sy = 1.25, 0.65  # 扁趴趴
            offset_y = 15

        elif state == "idle":
            # 微呼吸 — 果冻微微颤动
            breath = math.sin(frame * 0.07) * 0.04
            sx = 1.0 - breath
            sy = 1.0 + breath

        elif state == "walk":
            # 完整的果冻跳跃周期：起跳拉伸 → 落地压扁 → 回弹抖动
            period = 10  # TEST: 原35，每10帧一跳
            phase = (frame % period) / period

            if phase < 0.35:        # 起跳 — 向上拉伸变窄变高
                t = phase / 0.35
                sx = 1.0 - 0.25 * t   # 挤窄
                sy = 1.0 + 0.40 * t   # 拉高
                offset_y = int(-15 * t)
            elif phase < 0.5:       # 下落 — 恢复
                t = (phase - 0.35) / 0.15
                sx = 0.75 + 0.25 * t
                sy = 1.40 - 0.15 * t
                offset_y = int(-15 * (1 - t))
            elif phase < 0.65:      # 触地压扁
                t = (phase - 0.5) / 0.15
                sx = 1.0 + 0.35 * t
                sy = 1.0 - 0.30 * t
                offset_y = 5
            else:                   # 回弹抖动（衰减正弦）
                t = (phase - 0.65) / 0.35
                decay = math.exp(-t * 6)
                wobble = math.sin(t * 20) * 0.15 * decay
                sx = 1.0 + wobble
                sy = 1.0 - wobble * 0.7
                offset_y = 0

        elif state == "happy":
            # 兴奋弹跳
            bounce = abs(math.sin(frame * 0.2)) * 0.2
            sx = 1.0 - bounce * 0.3
            sy = 1.0 + bounce * 0.5
            offset_y = int(-bounce * 10)
            Slime._hearts(p, bw, bh, s, frame)

        elif state == "drag":
            # 被拎起来 — 拉长
            sx = 0.85
            sy = 1.2
            offset_y = 0

        # ========== 渲染 ==========
        p.save()
        # 以身体中心为轴心做缩放
        center_x = Slime.CANVAS // 2
        center_y = Slime.CANVAS // 2
        p.translate(center_x, center_y)
        p.scale(sx, sy)
        p.translate(-center_x, -center_y)

        ox = (Slime.CANVAS - bw) // 2
        oy = (Slime.CANVAS - bh) // 2 + offset_y

        Slime._render(p, px, ox, oy, s, frame, state, tint_palette)
        p.restore()

        p.end()
        return pix

    @staticmethod
    def _render(p, px, ox, oy, s, frame, state, palette):
        # 自动找出最深色 -> 默认当作眼睛（用于眨眼）
        darkest = min(palette.keys(),
                      key=lambda k: palette[k].red() + palette[k].green() + palette[k].blue())

        for r, row in enumerate(px):
            for c, ch in enumerate(row):
                if ch == '.' or ch not in palette:
                    continue
                color = palette[ch]
                p.setBrush(color)
                p.setPen(Qt.NoPen)

                if state in ("idle", "walk", "happy") and ch == darkest:
                    blink = frame > 30 and (frame % 65) < 3  # 前30帧冷却，之后每65帧眨3帧
                    if blink:
                        p.setBrush(QColor(40, 80, 40))
                        p.drawRect(ox + c * s, oy + r * s + s // 2 - 1, s, 2)
                        continue

                p.drawRect(ox + c * s, oy + r * s, s, s)

    @staticmethod
    def _rgb_to_hsl(r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx, mn = max(r, g, b), min(r, g, b)
        l = (mx + mn) / 2
        if mx == mn:
            h = s = 0.0
        else:
            d = mx - mn
            s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
            if mx == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif mx == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0
            h /= 6.0
        return h, s, l

    @staticmethod
    def _hsl_to_rgb(h, s, l):
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        return int(r * 255), int(g * 255), int(b * 255)

    @staticmethod
    def _hearts(p, bw, bh, s, frame):
        cx = Slime.CANVAS // 2
        cy = Slime.CANVAS // 2 - bh // 2
        p.setPen(QPen(QColor(255, 80, 120), 2))
        hearts = [
            (cx - bw//3,     cy - 3,  int(6 + math.sin(frame * 0.15) * 2)),
            (cx + bw//3 - 4, cy - 8,  int(5 + math.sin(frame * 0.22 + 1) * 2)),
            (cx,             cy - 16, int(4 + math.sin(frame * 0.27) * 2)),
        ]
        for hx, hy, sz in hearts:
            f = QFont("Arial", sz)
            p.setFont(f)
            p.drawText(QRect(hx - sz, hy - sz, sz * 3, sz * 3), Qt.AlignCenter, "♥")


_load_custom_skins()  # 加载用户自制皮肤
apply_skin(0)  # 默认紫晶史莱姆

# ====================================================
#  全局宠物管理
# ====================================================
PETS = []  # 所有活着的史莱姆

def _all_pets_switch_skin(idx):
    for pet in PETS:
        pet._switch_skin(idx)

def _skin_icon(skin, size=48):
    """生成皮肤缩略图"""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, False)
    idle = skin["idle"]
    pal = skin["palette"]
    cell = size / max(len(idle[0]), len(idle))
    ox = (size - len(idle[0]) * cell) // 2
    oy = (size - len(idle) * cell) // 2
    for r, row in enumerate(idle):
        for c, ch in enumerate(row):
            if ch == '.' or ch not in pal: continue
            p.setBrush(pal[ch])
            p.setPen(Qt.NoPen)
            p.drawRect(int(ox + c * cell), int(oy + r * cell), int(cell + 1), int(cell + 1))
    p.end()
    return QIcon(px)

PIXEL_MENU_STYLE = """
    QMenu {
        background: #16213e;
        border: 3px solid #0f3460;
        padding: 4px 2px;
        font-family: 'Consolas', 'Microsoft YaHei';
        font-size: 13px;
        color: #e0f7fa;
        image-rendering: pixelated;
    }
    QMenu::item {
        padding: 7px 20px 7px 10px;
        border: 2px solid transparent;
        margin: 1px 3px;
    }
    QMenu::item:selected {
        background: #0f3460;
        border: 2px solid #00e5ff;
        color: #00e5ff;
    }
    QMenu::separator {
        height: 2px;
        background: #0f3460;
        margin: 3px 8px;
    }
"""

# ====================================================
#  桌面窗口
# ====================================================

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        PETS.append(self)  # 注册到全局
        self._state = "idle"
        self._frame = 0
        self._pet_scale = 1.0  # 体型缩放（生崽会变小）
        self._spawn_count = 0  # 已生崽次数，最多3次
        self._chasing = False  # 正在追鼠标
        self._grow = 0  # 双击变大
        self._angry = 0  # 生气倒计时
        self._drag_count = 0  # 连续拖拽次数
        self._drag_timer = 0  # 拖拽计时器
        self._countdown = random.randint(180, 350)
        self._dragging = False
        self._drag_offset = QPoint()
        self._tx = None; self._ty = None
        self._inactive = 0

        self.setWindowTitle("My Slime")
        self.setFixedSize(Slime.CANVAS, Slime.CANVAS + 70)  # 顶部留空间给气泡
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAcceptDrops(True)  # 接受文件拖放

        self._mode = "active"
        self._mode_names = {"active": "活跃模式", "quiet": "安静模式", "hunt": "贪吃模式"}
        self._fish_submode = "visual"  # visual / timed
        self._fish_running = False
        self._fish_submode_names = {"visual": "视觉检测", "timed": "定时抛竿"}
        self._bubble_text = ""  # 聊天框文字
        self._bubble_timer = 0  # 消失倒计时

        self._anim = QTimer(self); self._anim.timeout.connect(self._tick); self._anim.start(50)
        self._bhv = QTimer(self); self._bhv.timeout.connect(self._behave); self._bhv.start(1000)

        # 背景色采样（变色龙效果）
        self.bg_color = None  # (r, g, b)
        self._color_timer = QTimer(self)
        self._color_timer.timeout.connect(self._sample_bg)
        self._color_timer.start(400)  # 每 0.4 秒采样一次

        # 托盘
        self.tray = QSystemTrayIcon(self)
        px = QPixmap(32, 32); px.fill(Qt.transparent)
        pp = QPainter(px)
        pp.setBrush(QColor(82, 200, 82)); pp.setPen(QPen(QColor(50, 150, 50), 2))
        pp.drawRect(6, 10, 20, 14)
        pp.setBrush(QColor(140, 250, 140)); pp.drawRect(10, 13, 12, 8)
        pp.setBrush(QColor(20, 35, 20))
        pp.drawRect(11, 14, 2, 2); pp.drawRect(13, 13, 2, 2)
        pp.drawRect(17, 14, 2, 2); pp.drawRect(19, 13, 2, 2)
        pp.end()
        self.tray.setIcon(QIcon(px)); self.tray.setToolTip("My Slime")
        self._hidden = False
        self._toggle_action = None
        self._autostart = os.path.exists(self._startup_path())

        m = QMenu()
        m.setStyleSheet(PIXEL_MENU_STYLE)
        m.addAction(f"切换模式 (当前: {self._mode_names[self._mode]})", self._cycle_mode)
        skin_menu = m.addMenu("选择皮肤")
        skin_menu.setStyleSheet(PIXEL_MENU_STYLE)
        for i, s in enumerate(SKINS):
            icon = _skin_icon(s)
            mark = " ◀" if i == SKIN_INDEX else ""
            action = skin_menu.addAction(icon, f"{s['name']}{mark}")
            action.triggered.connect(lambda checked, idx=i: self._switch_skin(idx))
            if i >= BUILTIN_COUNT:
                skin_menu.addAction(f"  ✕ 删除 {s['name']}").triggered.connect(
                    lambda checked, idx=i: _delete_custom_skin(idx))
        skin_menu.addSeparator()
        skin_menu.addAction("＋ 导入皮肤", self._import_skin)
        skin_menu.addAction("＋ 画新皮肤", self._open_editor)
        # 歪瓜子菜单
        hack_menu = m.addMenu("歪瓜")
        hack_menu.addAction("开始钓鱼 (视觉)", lambda: self._start_fish("visual"))
        hack_menu.addAction("开始钓鱼 (定时)", lambda: self._start_fish("timed"))
        hack_menu.addAction("停止钓鱼", self._stop_fishing)
        hack_menu.addSeparator()
        hack_menu.addAction("连点器...", self._auto_clicker_dialog)
        m.addSeparator()
        m.addAction("喂食", self._feed)
        m.addAction(f"生一只 ({3 - self._spawn_count}/3)", self._spawn_child)
        if self._find_nearby():
            m.addAction("合体", self._fusion)
        m.addAction("重置", self._reset)
        m.addSeparator()
        m.addAction("打开回收站 🗑️", self._open_trash)
        m.addSeparator()
        self._toggle_action = m.addAction("隐藏 (打游戏时点这里)")
        self._toggle_action.triggered.connect(self._toggle_visible)
        m.addAction("检查更新", self._check_update)
        m.addAction("关于", self._show_about)
        self._autostart_action = m.addAction(f"{'☑' if self._autostart else '☐'} 开机自启")
        self._autostart_action.triggered.connect(self._toggle_autostart)
        m.addAction("退出", self._quit)
        self.tray.setContextMenu(m); self.tray.show()

        geo = QApplication.primaryScreen().availableGeometry()
        self.move(geo.right() - 170, geo.bottom() - 180)

    def _tick(self):
        self._frame += 1
        # 生气倒计时
        if self._angry > 0:
            self._angry -= 1
            if self._angry == 0:
                self._bubble_text = "哼，原谅你了"
                self._bubble_timer = 30
        # 拖拽计时
        if self._drag_timer > 0:
            self._drag_timer -= 1
            if self._drag_timer == 0:
                self._drag_count = 0
        # 连续拖拽3次以上 → 生气！
        if self._drag_count >= 3 and self._angry == 0 and self.state == "drag":
            self._angry = 120  # 生气60帧=1.2秒? no 要60秒=3600帧
            self._angry = 400  # 20秒 = 20fps*20
            msgs = ["别碰我！！！", "生气了！！", "走开！！", "再碰我就跑啦！", "烦死了！"]
            self._bubble_text = random.choice(msgs)
            self._bubble_timer = 90
            self._drag_count = 0
        # 双击变大
        if self._grow > 0:
            self._grow -= 1
        if self._tx is not None and self.state == "walk":
            self._step()

        # 活跃模式：随机追鼠标
        if self._mode == "active" and self._chasing and self.state == "idle" and self._frame % 3 == 0:
            mx = QCursor.pos().x(); my = QCursor.pos().y()
            cx = self.x() + self.width()//2; cy = self.y() + self.height()//2
            dx = mx - cx; dy = my - cy
            dist = math.hypot(dx, dy)
            if dist < 30:
                # 追到了！拖拽鼠标
                self._chasing = False
                pyautogui.moveRel(random.randint(-20, 20), random.randint(-20, 20))
                self._bubble_text = "抓到你了！"
                self._bubble_timer = 40
            else:
                s = min(3, dist / 30)
                nx = self.x() + int(dx/dist * s)
                ny = self.y() + int(dy/dist * s)
                geo = QApplication.primaryScreen().availableGeometry()
                nx = max(geo.left(), min(nx, geo.right() - self.width()))
                ny = max(geo.top(), min(ny, geo.bottom() - self.height()))
                self.move(nx, ny)

        # 鼠标靠近就大跳逃跑 + 聊天气泡
        if self.state == "idle" and self._mode != "quiet" and not self._chasing and self._frame % 6 == 0:
            mx = QCursor.pos().x()
            my = QCursor.pos().y()
            cx = self.x() + self.width() // 2
            cy = self.y() + self.height() // 2
            dx = cx - mx
            dy = cy - my
            dist = math.hypot(dx, dy)
            escape_dist = 130
            if dist < escape_dist and dist > 0:
                # 往远跳
                jump_dist = random.randint(150, 300)
                self._tx = self.x() + int(dx / dist * jump_dist)
                self._ty = self.y() + int(dy / dist * jump_dist)
                geo = QApplication.primaryScreen().availableGeometry()
                self._tx = max(geo.left(), min(self._tx, geo.right() - self.width()))
                self._ty = max(geo.top(), min(self._ty, geo.bottom() - self.height()))
                self.state = "walk"
                self._inactive = 0
                # 5% 几率嘴炮
                if random.random() < 0.05:
                    msgs = ["你跑不过我你信不信", "追不到我~", "略略略~", "来抓我呀！",
                            "太慢了！", "哈哈哈哈", "跑得真慢", "加油追上我呀"]
                    self._bubble_text = random.choice(msgs)
                    self._bubble_timer = 60

        # 史莱姆靠近时轻轻挤开
        if self.state != "drag" and self._frame % 5 == 0:
            for other in PETS:
                if other is self or other._hidden: continue
                cx1, cy1 = self.x()+self.width()//2, self.y()+self.height()//2
                cx2, cy2 = other.x()+other.width()//2, other.y()+other.height()//2
                dx, dy = cx1-cx2, cy1-cy2
                dist = math.hypot(dx, dy)
                # 碰撞距离随体型缩放
                collide_dist = 100 * (self._pet_scale + other._pet_scale) / 2
                if dist < collide_dist and dist > 0:
                    push = 2
                    geo = QApplication.primaryScreen().availableGeometry()
                    nx = self.x() + int(dx/dist * push)
                    ny = self.y() + int(dy/dist * push)
                    self.move(max(geo.left(), min(nx, geo.right()-self.width())),
                              max(geo.top(), min(ny, geo.bottom()-self.height())))
                    self._tx = None

        # 气泡倒计时
        if self._bubble_timer > 0:
            self._bubble_timer -= 1
            if self._bubble_timer == 0:
                self._bubble_text = ""

        self.update()

    def _behave(self):
        self._inactive += 1
        # 活跃模式：每分钟5%概率追鼠标
        if self._mode == "active" and not self._chasing and self._inactive % 60 == 0:
            if random.random() < 0.05:
                self._chasing = True
                self._bubble_text = "我来抓你啦！"
                self._bubble_timer = 30
        # 19% 几率自言自语
        if self.state == "idle" and not self._bubble_text and random.random() < 0.19:
            msgs = ["啊", "啊啊啊", "啊~", "啊啊", "啊！", "啊？", "啊...",
                    "啊啊啊啊", "啊哈~", "啊啊啊！"]
            self._bubble_text = random.choice(msgs)
            self._bubble_timer = 45  # 显示2秒多
        if self.state in ("drag", "happy", "surprise", "eat"):
            self._inactive = 0; return
        if self.state == "idle":
            self._countdown -= 1
            if self._countdown <= 0:
                if self._mode == "quiet" or self._chasing:
                    pass  # 安静/追鼠标中：不自动走动
                elif self._mode == "hunt":
                    if random.random() < 0.9:
                        self._go_nearby()  # 贪吃模式：频繁小范围走动
                else:
                    if random.random() < 0.6:
                        self._go()  # 活跃模式：正常走动
                self._countdown = {"active": random.randint(150, 350),
                                   "quiet": 9999,
                                   "hunt": random.randint(30, 80)}[self._mode]
                self._inactive = 0
        if self._inactive > 600 and self._mode != "hunt":
            self.state = "sleep"

    def _go(self):
        geo = QApplication.primaryScreen().availableGeometry()
        m = 50
        self._tx = random.randint(geo.left() + m, geo.right() - m - Slime.CANVAS)
        self._ty = random.randint(geo.top() + m, geo.bottom() - m - Slime.CANVAS - 40)
        self.state = "walk"

    def _go_nearby(self):
        """贪吃模式：在当前位置附近小范围走动"""
        geo = QApplication.primaryScreen().availableGeometry()
        self._tx = self.x() + random.randint(-60, 60)
        self._ty = self.y() + random.randint(-60, 60)
        self._tx = max(geo.left(), min(self._tx, geo.right() - Slime.CANVAS))
        self._ty = max(geo.top(), min(self._ty, geo.bottom() - Slime.CANVAS - 40))
        self.state = "walk"

    def _switch_skin(self, idx):
        apply_skin(idx)
        self._reset()
        # 更新托盘图标颜色（用调色板第一个非'-'颜色）
        colors = [c for k, c in PALETTE.items() if k != '-']
        if colors:
            c = colors[len(colors)//2]
            px = QPixmap(32, 32); px.fill(Qt.transparent)
            pp = QPainter(px); pp.setBrush(c); pp.setPen(QPen(c.darker(130), 2))
            pp.drawRect(6, 10, 20, 14); pp.end()
            self.tray.setIcon(QIcon(px))
        print(f"皮肤切换为: {SKINS[idx]['name']}")

    def _cycle_mode(self):
        keys = list(self._mode_names.keys())
        idx = keys.index(self._mode)
        self._mode = keys[(idx + 1) % len(keys)]
        self._reset()
        self.tray.setToolTip(f"Slime ({self._mode_names[self._mode]})")

    def _toggle_fish_submode(self):
        """切换钓鱼子模式：视觉 ↔ 定时"""
        if self._fish_submode == "visual":
            self._fish_submode = "timed"
        else:
            self._fish_submode = "visual"
        print(f"钓鱼子模式切换为: {self._fish_submode_names[self._fish_submode]}")

    def _step(self):
        if self._tx is None: return
        dx = self._tx - self.x(); dy = self._ty - self.y()
        d = math.hypot(dx, dy)
        if d < 5:
            self.move(self._tx, self._ty); self._tx = None; self._ty = None
            self.state = "idle"; self._countdown = 20  # TEST: 原random.randint(180,400)
            return
        s = 2.5
        self.move(self.x() + int(dx / d * s), self.y() + int(dy / d * s))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self._angry > 0: return  # 生气中不理你
            self._dragging = True; self._drag_offset = e.pos(); self.state = "drag"
            self._drag_count += 1
            self._drag_timer = 180  # 3秒内连续拖拽算

    def mouseMoveEvent(self, e):
        if self._dragging:
            self.move(e.globalPos() - self._drag_offset)
            self._tx = None; self._ty = None

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._dragging = False; self.state = "idle"
            self._countdown = random.randint(180, 400); self._inactive = 0

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton and self._angry == 0:
            self._grow = 30

    # ---- 文件拖放（表情位预留，待朋友画 SURPRISE_PX / EAT_PX）----
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._set_s("surprise")  # TODO: 替换为 SURPRISE_PX 表情
            self._inactive = 0

    def dragLeaveEvent(self, e):
        self._set_s("idle")

    def dropEvent(self, e):
        self._set_s("eat")
        QTimer.singleShot(1500, lambda: self._set_s("idle"))
        # 把文件丢进回收站
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path and os.path.exists(path):
                try:
                    subprocess.Popen([
                        "powershell", "-Command",
                        f"Add-Type -AssemblyName Microsoft.VisualBasic;"
                        f"[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('{path}',"
                        f"'OnlyErrorDialogs','SendToRecycleBin')"
                    ], shell=True)
                    print(f"Eaten -> recycle bin: {os.path.basename(path)}")
                except Exception as err:
                    print(f"Failed to delete: {err}")

    def contextMenuEvent(self, e):
        m = QMenu(self)
        m.setStyleSheet(PIXEL_MENU_STYLE)
        m.addAction(f"切换模式 (当前: {self._mode_names[self._mode]})", self._cycle_mode)
        skin_menu = m.addMenu("选择皮肤")
        skin_menu.setStyleSheet(PIXEL_MENU_STYLE)
        for i, s in enumerate(SKINS):
            icon = _skin_icon(s)
            mark = " ◀" if i == SKIN_INDEX else ""
            action = skin_menu.addAction(icon, f"{s['name']}{mark}")
            action.triggered.connect(lambda checked, idx=i: self._switch_skin(idx))
            if i >= BUILTIN_COUNT:
                skin_menu.addAction(f"  ✕ 删除 {s['name']}").triggered.connect(
                    lambda checked, idx=i: _delete_custom_skin(idx))
        skin_menu.addSeparator()
        skin_menu.addAction("＋ 导入皮肤", self._import_skin)
        skin_menu.addAction("＋ 画新皮肤", self._open_editor)
        hack_menu = m.addMenu("歪瓜")
        hack_menu.addAction("开始钓鱼 (视觉)", lambda: self._start_fish("visual"))
        hack_menu.addAction("开始钓鱼 (定时)", lambda: self._start_fish("timed"))
        hack_menu.addAction("停止钓鱼", self._stop_fishing)
        hack_menu.addSeparator()
        hack_menu.addAction("连点器...", self._auto_clicker_dialog)
        m.addSeparator()
        m.addAction("喂食", self._feed)
        m.addAction(f"生一只 ({3 - self._spawn_count}/3)", self._spawn_child)
        if self._find_nearby():
            m.addAction("合体", self._fusion)
        m.addAction("重置", self._reset)
        m.addSeparator()
        m.addAction("打开回收站 🗑️", self._open_trash)
        m.addSeparator()
        m.addAction("检查更新", self._check_update)
        m.addAction("关于", self._show_about)
        m.addAction("隐藏" if not self._hidden else "显示", self._toggle_visible)
        m.addAction(f"{'☑' if self._autostart else '☐'} 开机自启", self._toggle_autostart)
        m.addAction("退出", self._quit)
        m.exec_(e.globalPos())

    def _feed(self):
        if self._angry > 0:
            self._angry = 0
            self._bubble_text = "原谅你了~"
            self._bubble_timer = 40
        else:
            self.state = "happy"; self._frame = 0; self._inactive = 0
            QTimer.singleShot(2000, lambda: self._set_s("idle"))

    def _reset(self):
        self.state = "idle"; self._frame = 0; self._inactive = 0
        self._countdown = random.randint(180, 400)

    def _toggle_visible(self):
        self._hidden = not self._hidden
        if self._hidden:
            self.hide()
            self._toggle_action.setText("显示")
            self.tray.setToolTip("Slime (已隐藏)")
        else:
            self.show()
            self._toggle_action.setText("隐藏 (打游戏时点这里)")
            self.tray.setToolTip("Slime")

    def _do_jump(self):
        """手动跳一下"""
        if self.state in ("drag",): return
        # 在当前位置做一个短跳跃：设近处目标触发 walk 动画
        self._tx = self.x() + random.randint(-30, 30)
        self._ty = self.y() + random.randint(-40, -10)
        self._tx = max(0, min(self._tx, QApplication.primaryScreen().availableGeometry().right() - self.width()))
        self._ty = max(0, self._ty)
        self.state = "walk"
        self._inactive = 0

    def _open_trash(self):
        """打开 Windows 回收站"""
        try:
            os.startfile("shell:RecycleBinFolder")
        except:
            subprocess.Popen(["explorer", "shell:RecycleBinFolder"])

    # ---- 钓一下（一次抛竿+收杆）----
    # ---- 歪瓜：钓鱼 ----
    def _start_fish(self, submode="visual"):
        """开启钓鱼（视觉/定时）"""
        self._fish_submode = submode
        if self._fish_running: return  # 已经在钓
        self._fish_running = True
        print(f"🎣 钓鱼开始 ({self._fish_submode_names[submode]})")
        threading.Thread(target=self._fish_loop, daemon=True).start()

    def _stop_fishing(self):
        self._fish_running = False

    def _fish_loop(self):
        while self._fish_running:
            try:
                if self._fish_submode == "timed":
                    self._fish_timed()
                else:
                    self._fish_visual()
            except Exception as e:
                print(f"Fish error: {e}")
                time.sleep(2)

    def _fish_timed(self):
        """定时模式：抛竿→随机等5~25秒→收杆"""
        pyautogui.rightClick()  # 抛竿
        time.sleep(random.uniform(5, 25))
        pyautogui.rightClick()  # 收杆
        time.sleep(random.uniform(1, 3))

    def _fish_visual(self):
        """视觉模式：抛竿→检测水花→收杆"""
        pyautogui.rightClick()
        time.sleep(1.2)
        x, y = pyautogui.position()
        for _ in range(350):
            if not self._fish_running: return
            time.sleep(0.1)
            try:
                img = pyautogui.screenshot(region=(x - 30, y - 30, 60, 60))
                arr = np.array(img, dtype=np.uint8)
                bright = np.count_nonzero(arr.max(axis=2) > 180)
                if bright / 3600 > 0.08:
                    pyautogui.rightClick()
                    print("Fish caught! (visual)")
                    break
            except:
                pass
        else:
            pyautogui.rightClick()
        time.sleep(random.uniform(1, 3))

    def _spawn_child(self):
        """生一只新的史莱姆，最多3次"""
        if self._spawn_count >= 3:
            self._bubble_text = "生不动了..."
            self._bubble_timer = 30
            return
        self._spawn_count += 1
        child = DesktopPet()
        child._switch_skin(SKIN_INDEX)
        child._pet_scale = self._pet_scale * 0.7
        self._pet_scale = child._pet_scale
        child._spawn_count = 0  # 下一代重置计数
        geo = QApplication.primaryScreen().availableGeometry()
        child.move(self.x() + random.randint(-60, 60),
                   self.y() + random.randint(-60, 60))
        child.show()
        print(f"生了一只小史莱姆！一共 {len(PETS)} 只")

    @staticmethod
    def _startup_path():
        return os.path.join(os.environ["APPDATA"],
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
            "start_slime.bat")

    def _open_editor(self):
        """打开浏览器画板"""
        editor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pixel_editor.html")
        os.startfile(editor_path)

    def _auto_clicker_dialog(self):
        """连点器对话框：设置次数和间隔"""
        from PyQt5.QtWidgets import QInputDialog
        count, ok1 = QInputDialog.getInt(self, "连点器", "点击次数:", 100, 1, 99999, 1)
        if not ok1: return
        interval, ok2 = QInputDialog.getInt(self, "连点器", "间隔(毫秒):", 100, 10, 5000, 10)
        if not ok2: return
        print(f"连点器：{count}次, 间隔{interval}ms, 3秒后开始...")
        self._bubble_text = f"点{count}下!"
        self._bubble_timer = 30
        threading.Thread(target=self._auto_clicker_run,
                         args=(count, interval / 1000.0), daemon=True).start()

    def _auto_clicker_run(self, count, interval):
        time.sleep(3)
        for i in range(count):
            if self._mode != "fish":  # 不钓鱼就不取消
                pyautogui.click()
                time.sleep(interval)

    def _import_skin(self):
        """粘贴代码导入皮肤"""
        from PyQt5.QtWidgets import QInputDialog, QTextEdit
        name, ok = QInputDialog.getText(self, "导入皮肤", "给皮肤起个名字:")
        if not ok or not name.strip(): return
        # 弹窗让用户粘贴代码
        d = QDialog(self)
        d.setWindowTitle("粘贴导出的代码")
        d.setFixedSize(500, 350)
        d.setStyleSheet("QDialog { background: #16213e; } QLabel { color: #e0f7fa; }")
        layout = QVBoxLayout(d)
        layout.addWidget(QLabel("把画板导出的 PALETTE + SLIME_PX 代码粘贴进来:"))
        text = QTextEdit()
        text.setStyleSheet("background: #1a1a2e; color: #8f8; font-family: Consolas; font-size: 11px;")
        layout.addWidget(text)
        btn = QPushButton("导入")
        btn.setStyleSheet("background: #0f3460; color: #00e5ff; padding: 8px; font-weight: bold;")
        btn.clicked.connect(d.accept)
        layout.addWidget(btn)
        if d.exec_():
            code = text.toPlainText().strip()
            if code:
                _save_custom_skin(name.strip(), code)
                apply_skin(len(SKINS) - 1)  # 切到刚导入的
                self._switch_skin(len(SKINS) - 1)

    def _check_update(self):
        """打开网站查看更新"""
        os.startfile("https://bailidashi.github.io")

    def _show_about(self):
        d = QDialog(self)
        d.setWindowTitle("关于 桌面史莱姆")
        d.setFixedSize(350, 460)
        d.setStyleSheet("""
            QDialog { background: #16213e; border: 3px solid #0f3460; }
            QLabel { color: #e0f7fa; font-family: 'Microsoft YaHei'; }
        """)
        layout = QVBoxLayout(d)
        layout.setSpacing(6)

        title = QLabel("桌面史莱姆 v2.0")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00e5ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(QLabel(""))

        info = QLabel("一只会走路、变色、钓鱼、生气、生崽的桌面宠物。\n像素点阵渲染，纯字符驱动图形。")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 12px; color: #a0c4d0;")
        layout.addWidget(info)
        layout.addWidget(QLabel(""))

        layout.addWidget(self._about_line("制作者", "百裏"))
        layout.addWidget(self._about_line("皮肤绘制", "百裏的朋友们"))
        layout.addWidget(self._about_line("技术栈", "Python + PyQt5"))
        layout.addWidget(self._about_line("皮肤", f"{len(SKINS)} 套"))
        layout.addWidget(QLabel(""))
        # 可点击链接
        site = QLabel('  网站：<a href="https://bailidashi.github.io" style="color:#00e5ff;">bailidashi.github.io</a>')
        site.setOpenExternalLinks(True)
        site.setStyleSheet("font-size: 13px;")
        layout.addWidget(site)
        gh = QLabel('  GitHub：<a href="https://github.com/bailidashi" style="color:#00e5ff;">github.com/bailidashi</a>')
        gh.setOpenExternalLinks(True)
        gh.setStyleSheet("font-size: 13px;")
        layout.addWidget(gh)
        layout.addWidget(QLabel(""))
        layout.addWidget(self._about_line("功能", "果冻物理 / 变色龙 / 钓鱼歪瓜"))
        layout.addWidget(self._about_line("", "多只碰撞 / 生气模式 / 开机自启"))
        layout.addWidget(QLabel(""))

        btn = QPushButton("关闭")
        btn.setStyleSheet(
            "QPushButton { background: #0f3460; color: #00e5ff; border: 2px solid #00e5ff; "
            "padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: #00e5ff; color: #16213e; }"
        )
        btn.clicked.connect(d.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        d.exec_()

    def _about_line(self, label, value):
        w = QLabel(f"  {label}：{value}")
        w.setStyleSheet("font-size: 13px;")
        return w

    def _toggle_autostart(self):
        sp = self._startup_path()
        if os.path.exists(sp):
            os.remove(sp)
            self._autostart = False
        else:
            # 直接写 .bat 到启动文件夹，不用 PowerShell
            bat = f'''@echo off
cd /d "d:\\skill\\desktop_pet"
start "" "{sys.executable.replace('.exe', 'w.exe')}" "d:\\skill\\desktop_pet\\pet.py"
'''
            with open(sp, 'w') as f:
                f.write(bat)
            self._autostart = True
        self._autostart_action.setText(f"{'☑' if self._autostart else '☐'} 开机自启")

    def _find_nearby(self):
        """检查附近有没有其他史莱姆"""
        for other in PETS:
            if other is self or other._hidden: continue
            dist = math.hypot(self.x()-other.x(), self.y()-other.y())
            if dist < 150: return True
        return False

    def _fusion(self):
        """合体：吃掉附近一只史莱姆，自己变大"""
        for other in PETS:
            if other is self or other._hidden: continue
            dist = math.hypot(self.x()-other.x(), self.y()-other.y())
            if dist < 150:
                self._pet_scale = min(3.0, self._pet_scale + other._pet_scale * 0.4)
                self._bubble_text = "合体成功！"
                self._bubble_timer = 60
                other._quit()
                return

    def _quit(self):
        PETS.remove(self)
        if not PETS:
            self.tray.hide(); QApplication.quit()
        else:
            self.close()

    def _set_s(self, s):
        if self.state not in ("drag",):  # 拖拽中不打断
            self.state = s

    @property
    def state(self): return self._state

    @state.setter
    def state(self, v):
        if self._state != v: self._state = v; self._frame = 0

    def _sample_bg(self):
        """截取史莱姆窗口旁边的一小块区域，取平均色"""
        try:
            x, y = self.x(), self.y()
            sx, sy = 10, 10  # 采样大小
            # 从窗口右下角外侧采样
            nx = x + self.width() + 8
            ny = y + self.height() + 8

            screen = QApplication.primaryScreen().availableGeometry()
            nx = max(screen.left(), min(nx, screen.right() - sx))
            ny = max(screen.top(), min(ny, screen.bottom() - sy))

            img = ImageGrab.grab(bbox=(nx, ny, nx + sx, ny + sy))
            pixels = list(img.getdata())
            r = sum(p[0] for p in pixels) // len(pixels)
            g = sum(p[1] for p in pixels) // len(pixels)
            b = sum(p[2] for p in pixels) // len(pixels)
            self.bg_color = (r, g, b)
            # 每10秒打印一次确认在工作
            if self._frame % 200 == 0:
                print(f"BG sample at ({nx},{ny}): RGB({r},{g},{b})")
        except Exception as e:
            print(f"Sample error: {e}")

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        scale = self._pet_scale
        if self._grow > 0:
            scale *= 1.0 + math.sin(self._grow / 30 * math.pi) * 0.4
        if scale != 1.0:
            p.translate(self.width()//2, self.height()//2)
            p.scale(scale, scale)
            p.translate(-self.width()//2, -self.height()//2)
        pix = Slime.make(self.state, self._frame, self.bg_color)
        # 生气时红色覆盖
        if self._angry > 0:
            p2 = QPainter(pix)
            p2.setCompositionMode(p2.CompositionMode_SourceAtop)
            p2.fillRect(pix.rect(), QColor(255, 40, 40, min(100, self._angry // 10)))
            p2.end()
        p.drawPixmap(0, 0, pix)

        # 画云朵聊天气泡
        if self._bubble_text and self._bubble_timer > 0:
            p.setRenderHint(QPainter.Antialiasing, True)
            text = self._bubble_text
            font = QFont("Microsoft YaHei", 10)
            font.setBold(True)
            p.setFont(font)
            # 中文字符每个约15px宽，多加余量
            tw = len(text) * 16 + 32
            th = 32
            bx = max(2, self.width() // 2 - tw // 2)
            if bx + tw > self.width():
                bx = 2
                tw = self.width() - 4
            by = 6

            # 气泡透明度渐变
            alpha = min(255, self._bubble_timer * 8)
            p.setBrush(QColor(255, 255, 255, alpha))
            p.setPen(QPen(QColor(180, 180, 200, alpha), 2))

            # 圆角矩形 + 底部三角
            p.drawRoundedRect(bx, by, tw, th, 14, 14)
            # 小三角
            tri_x = self.width() // 2
            tri_y = by + th
            p.drawPolygon(
                QPoint(tri_x - 8, tri_y),
                QPoint(tri_x + 8, tri_y),
                QPoint(tri_x, tri_y + 8)
            )
            # 文字
            p.setPen(QColor(60, 60, 80, alpha))
            p.drawText(bx - 4, by + 2, tw + 8, th, Qt.AlignCenter, text)
            p.setRenderHint(QPainter.Antialiasing, False)

        p.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    pet = DesktopPet()
    pet.show()
    print("Your custom slime is running!")
    sys.exit(app.exec_())
