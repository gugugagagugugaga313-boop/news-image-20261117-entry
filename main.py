"""News image for 17 November 2026.

Draws a one-page newspaper front page for Tuesday 17 November 2026:
a masthead naming the date, plus six labelled story panels covering
the day's most consequential news across regions and fields, and a
footer ticker of three more verified items from the same day.

Pure standard library: the PNG is encoded by hand (zlib + struct),
text is rasterised from a small built-in 5x7 bitmap font, and every
picture is drawn from rectangles, lines, circles and polygons.
No network, no randomness, no wall clock: two runs write identical bytes.

Stories (all reported on 17 November 2026):
  1. Ukraine badly damaged the Kerch (Crimea) bridge for a second
     day; Russia struck Kyiv's two bridges over the Dnipro.
  2. Tankers hit mines near the Strait of Hormuz; a third US carrier
     reached the region; Iran fired drones at a US radar base in
     Bahrain, which Bahrain said were intercepted.
  3. China confirmed Xi, Trump and Putin meet in Shenzhen on
     Thursday 19 November, on the APEC sidelines.
  4. Japan scrambled fighter jets after suspected Russian aircraft
     entered its airspace; South Korea scrambled jets too.
  5. The Pentagon failed its financial audit for a ninth straight
     year; $4.8 trillion in assets could not be verified.
  6. Five European nations plan a joint migrant return facility
     in Rwanda for rejected asylum seekers.
Footer: SpaceX caught Starship's upper stage; WHO validated
Eritrea's elimination of trachoma; Germany beat the Netherlands 5-0.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# --- palette -----------------------------------------------------------
PAPER = (246, 241, 227)
NAVY = (20, 36, 62)
NAVY_DARK = (13, 25, 44)
GOLD = (227, 168, 28)
GOLD_DARK = (176, 124, 12)
WHITE = (255, 255, 255)
INK = (24, 24, 24)
GREY = (90, 90, 90)
LIGHT_GREY = (220, 220, 214)
RED = (169, 50, 38)
SEA = (214, 234, 248)
SEA_DEEP = (93, 173, 226)
SAND = (253, 235, 208)
MINT = (213, 245, 227)
MIST = (242, 243, 244)
ORANGE = (230, 126, 34)
YELLOW = (244, 208, 63)
TEAL = (26, 82, 118)
PURPLE = (108, 52, 131)
GREEN = (20, 90, 50)
SLATE = (46, 64, 83)

# --- 5x7 bitmap font: each glyph is 7 rows of 5 bits --------------------
FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "%": (25, 26, 2, 4, 8, 22, 19),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "+": (0, 4, 4, 14, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "?": (14, 17, 1, 2, 4, 0, 4),
    "!": (4, 4, 4, 4, 4, 0, 4),
    '"': (10, 10, 0, 0, 0, 0, 0),
    "*": (0, 21, 14, 21, 0, 0, 0),
    "\u2022": (0, 0, 12, 12, 12, 0, 0),
    "\u2014": (0, 0, 0, 14, 0, 0, 0),
}

BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def border(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, color, t=2):
        for ox in range(t):
            for oy in range(t):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, color)

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle_outline(self, cx, cy, r, color, t=2):
        for a in range(360):
            rad = math.radians(a)
            for k in range(t):
                self.set_pixel(
                    cx + int((r + k) * math.cos(rad)),
                    cy + int((r + k) * math.sin(rad)),
                    color,
                )

    def fill_polygon(self, points, color):
        """Scanline fill (even-odd) for a simple polygon."""
        if not points:
            return
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa = int(math.ceil(xs[j]))
                xb = int(math.floor(xs[j + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, color)

    def burst(self, cx, cy, r, color):
        self.fill_circle(cx, cy, max(2, r // 3), YELLOW)
        for a in range(0, 360, 30):
            rad = math.radians(a)
            self.thick_line(
                cx, cy,
                cx + int(r * math.cos(rad)),
                cy + int(r * math.sin(rad)),
                color, 2,
            )

    def draw_glyph(self, ch, x, y, scale, color, bold=False):
        glyph = FONT.get(ch, BLANK)
        extra = 1 if bold else 0
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    px = x + col * scale
                    py = y + row * scale
                    self.fill_rect(px, py, scale + extra, scale, color)

    def draw_text(self, text, x, y, scale, color, bold=False):
        cx = x
        for ch in text:
            self.draw_glyph(ch, cx, y, scale, color, bold)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, text, cx, y, scale, color, bold=False):
        self.draw_text(text, cx - text_width(text, scale) // 2, y, scale, color, bold)


# --- icons: each draws inside a scene rect (x, y, w, h) ------------------
def icon_bridge(cv, x, y, w, h):
    cv.fill_rect(x, y + h - 16, w, 16, SEA_DEEP)
    deck_y = y + h - 26
    mid = x + w // 2
    cv.fill_rect(x + 24, deck_y, mid - x - 42, 6, NAVY)
    cv.fill_rect(mid + 18, deck_y, x + w - 24 - (mid + 18), 6, NAVY)
    for tx in (x + 92, x + w - 100):
        cv.fill_rect(tx, y + 8, 8, deck_y - y - 8, NAVY)
        cv.fill_rect(tx - 6, y + 14, 20, 4, NAVY)
    cv.line(x + 96, y + 10, mid - 20, deck_y, GREY)
    cv.line(x + w - 96, y + 10, mid + 20, deck_y, GREY)
    cv.line(x + 96, y + 10, x + 30, deck_y, GREY)
    cv.line(x + w - 96, y + 10, x + w - 30, deck_y, GREY)
    cv.burst(mid, deck_y - 6, 16, ORANGE)
    cv.fill_circle(mid - 14, deck_y - 22, 7, GREY)
    cv.fill_circle(mid + 10, deck_y - 28, 9, GREY)


def icon_tanker(cv, x, y, w, h):
    cv.fill_rect(x, y + h - 12, w, 12, SEA_DEEP)
    cv.fill_rect(x + 30, y + h - 16, w - 60, 3, WHITE)
    hull = [
        (x + 60, y + 30), (x + w - 60, y + 30),
        (x + w - 90, y + 52), (x + 90, y + 52),
    ]
    cv.fill_polygon(hull, NAVY_DARK)
    cv.fill_rect(x + 120, y + 12, 26, 18, RED)
    cv.fill_rect(x + 150, y + 12, 26, 18, GOLD)
    cv.fill_rect(x + 180, y + 12, 26, 18, TEAL)
    cv.fill_rect(x + w - 130, y + 16, 10, 14, GREY)
    mx, my = x + w - 56, y + 14
    cv.fill_circle(mx, my, 8, INK)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        cv.line(mx, my, mx + int(13 * math.cos(rad)),
                my + int(13 * math.sin(rad)), INK)
    cv.fill_rect(x + 40, y + h - 20, 34, 3, WHITE)
    cv.fill_rect(x + w - 74, y + h - 20, 34, 3, WHITE)


def icon_summit(cv, x, y, w, h):
    cv.fill_rect(x, y + h - 8, w, 3, GOLD_DARK)
    poles = [x + 110, x + w // 2, x + w - 130]
    # United States: red field, white stripes, blue canton.
    fx, fy = poles[0], y + 6
    cv.fill_rect(fx, fy, 52, 30, RED)
    for s in range(3):
        cv.fill_rect(fx, fy + 5 + s * 10, 52, 4, WHITE)
    cv.fill_rect(fx, fy, 22, 14, NAVY)
    # China: red field, yellow stars.
    fx = poles[1] - 26
    cv.fill_rect(fx, fy, 52, 30, RED)
    cv.fill_circle(fx + 10, fy + 9, 4, YELLOW)
    cv.fill_circle(fx + 24, fy + 7, 2, YELLOW)
    cv.fill_circle(fx + 30, fy + 14, 2, YELLOW)
    cv.fill_circle(fx + 24, fy + 21, 2, YELLOW)
    cv.fill_circle(fx + 14, fy + 20, 2, YELLOW)
    # Russia: white, blue, red stripes.
    fx = poles[2] - 26
    cv.fill_rect(fx, fy, 52, 10, WHITE)
    cv.fill_rect(fx, fy + 10, 52, 10, TEAL)
    cv.fill_rect(fx, fy + 20, 52, 10, RED)
    for px in poles:
        cv.line(px, y + 4, px, y + h - 8, NAVY_DARK)
    cv.draw_text("US  CN  RU", x + w // 2 - 66, y + h - 24, 2, NAVY_DARK, bold=True)


def icon_jets(cv, x, y, w, h):
    cv.fill_circle(x + 74, y + 30, 17, RED)
    jet = [
        (x + 250, y + 22), (x + 330, y + 34), (x + 250, y + 40),
        (x + 272, y + 34),
    ]
    cv.fill_polygon(jet, NAVY_DARK)
    cv.fill_polygon(
        [(x + 250, y + 22), (x + 296, y + 30), (x + 250, y + 34)], SLATE)
    for ly, lx in ((y + 26, 120), (y + 38, 96), (y + 50, 130)):
        cv.fill_rect(x + lx, ly, 70, 3, WHITE)
    cv.draw_text("JAPAN", x + 330, y + 46, 2, NAVY_DARK, bold=True)


def icon_audit(cv, x, y, w, h):
    dx, dy = x + 150, y + 6
    cv.fill_rect(dx, dy, 120, 54, WHITE)
    cv.border(dx, dy, 120, 54, NAVY, 2)
    for i in range(4):
        cv.fill_rect(dx + 10, dy + 9 + i * 11, 100 - i * 18, 4, GREY)
    cx, cy = x + 330, y + 32
    cv.circle_outline(cx, cy, 22, RED, 3)
    cv.draw_text("9", cx - 8, cy - 11, 3, RED, bold=True)
    cv.draw_text("9TH YEAR", x + 40, y + 44, 2, RED, bold=True)


def icon_hub(cv, x, y, w, h):
    cx, cy = x + w // 2, y + 30
    spots = [
        (x + 60, y + 12, RED), (x + 130, y + 46, TEAL),
        (x + w - 140, y + 12, GOLD_DARK), (x + w - 70, y + 44, PURPLE),
        (x + 260, y + 10, GREEN),
    ]
    for sx, sy, col in spots:
        cv.line(sx, sy, cx, cy, GREY)
        cv.fill_circle(sx, sy, 6, col)
    cv.fill_circle(cx, cy, 13, RED)
    cv.fill_polygon([(cx - 11, cy + 8), (cx + 11, cy + 8), (cx, cy + 26)], RED)
    cv.fill_circle(cx, cy - 2, 5, WHITE)
    cv.draw_text("5 NATIONS, 1 HUB", x + 8, y + h - 16, 2, NAVY_DARK, bold=True)


# --- stories -------------------------------------------------------------
PANELS = [
    {
        "kicker": "EUROPE - WAR", "color": RED, "icon": icon_bridge,
        "bg": SEA, "headline": "CRIMEA BRIDGE HIT AGAIN",
        "body": "UKRAINE BADLY DAMAGED THE KERCH BRIDGE FOR A SECOND DAY "
                "RUNNING. ZELENSKYY HAILED AN UNPRECEDENTED OPERATION. "
                "RUSSIA HIT KYIV'S TWO BRIDGES OVER THE DNIPRO.",
    },
    {
        "kicker": "MIDDLE EAST", "color": TEAL, "icon": icon_tanker,
        "bg": SEA, "headline": "TANKERS HIT BY MINES",
        "body": "TANKERS STRUCK MINES NEAR THE STRAIT OF HORMUZ. A THIRD "
                "US CARRIER REACHED THE REGION. IRAN FIRED DRONES AT A US "
                "RADAR BASE IN BAHRAIN; BAHRAIN SAID THEY WERE INTERCEPTED.",
    },
    {
        "kicker": "ASIA - DIPLOMACY", "color": GOLD_DARK, "icon": icon_summit,
        "bg": SAND, "headline": "XI, TRUMP, PUTIN TO MEET",
        "body": "CHINA CONFIRMED THE THREE LEADERS WILL MEET IN SHENZHEN "
                "ON THURSDAY 19 NOVEMBER, ON THE SIDELINES OF THE APEC "
                "SUMMIT. TRUMP IS TRAVELLING TO ASIA.",
    },
    {
        "kicker": "ASIA - SECURITY", "color": SLATE, "icon": icon_jets,
        "bg": SEA, "headline": "JETS SCRAMBLED",
        "body": "JAPAN LAUNCHED FIGHTER JETS AND PROTESTED STRONGLY AFTER "
                "SUSPECTED RUSSIAN AIRCRAFT ENTERED ITS AIRSPACE. SOUTH "
                "KOREA ALSO SCRAMBLED JETS.",
    },
    {
        "kicker": "USA", "color": PURPLE, "icon": icon_audit,
        "bg": MIST, "headline": "PENTAGON FAILS AUDIT",
        "body": "AUDITORS FAILED THE PENTAGON'S BOOKS FOR A NINTH STRAIGHT "
                "YEAR. THEY COULD NOT VERIFY ACCOUNTS COVERING MORE THAN "
                "$4.8 TRILLION IN ASSETS.",
    },
    {
        "kicker": "EUROPE - MIGRATION", "color": GREEN, "icon": icon_hub,
        "bg": MINT, "headline": "RWANDA RETURN HUB",
        "body": "GERMANY, DENMARK, AUSTRIA, GREECE AND THE NETHERLANDS "
                "PLAN A JOINT RETURN FACILITY IN RWANDA FOR REJECTED "
                "ASYLUM SEEKERS.",
    },
]

FOOTER = ("ALSO: SPACEX CATCHES STARSHIP \u2022 ERITREA ENDS TRACHOMA "
          "\u2022 GERMANY 5-0 NETHERLANDS")
STRIP = "BRIDGES BURN  \u2022  TANKERS MINED  \u2022  SUMMIT SET  \u2022  JETS SCRAMBLED"


def draw_panel(cv, x, y, w, h, panel):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, NAVY, 2)
    pad = 12
    inner = w - 2 * pad
    # Kicker chip.
    chip_w = text_width(panel["kicker"], 2) + 16
    cv.fill_rect(x + pad, y + 10, chip_w, 24, panel["color"])
    cv.draw_text(panel["kicker"], x + pad + 8, y + 15, 2, WHITE, bold=True)
    # Icon scene.
    ix, iy, iw, ih = x + pad, y + 42, inner, 64
    cv.fill_rect(ix, iy, iw, ih, panel["bg"])
    cv.border(ix, iy, iw, ih, LIGHT_GREY, 1)
    panel["icon"](cv, ix, iy, iw, ih)
    # Headline, up to two lines.
    lines = wrap_text(panel["headline"], 3, inner)
    hy = y + 118
    for line in lines[:2]:
        cv.draw_text(line, x + pad, hy, 3, INK, bold=True)
        hy += 26
    # Body, up to five lines.
    body = wrap_text(panel["body"], 2, inner)
    by = hy + 8
    for line in body[:5]:
        cv.draw_text(line, x + pad, by, 2, INK)
        by += 16


def build():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.fill_rect(0, 0, W, 148, NAVY)
    cv.draw_text_centered("THE WORLD IN ONE PICTURE", W // 2, 20, 2, GOLD, bold=True)
    cv.draw_text_centered("17 NOVEMBER 2026", W // 2, 48, 7, WHITE, bold=True)
    cv.draw_text_centered("TUESDAY", W // 2, 110, 3, GOLD, bold=True)
    # Gold strip.
    cv.fill_rect(0, 148, W, 28, GOLD)
    cv.draw_text_centered(STRIP, W // 2, 155, 2, NAVY, bold=True)
    # Six story panels, two columns by three rows.
    col_w = 490
    row_y = [188, 452, 716]
    row_h = 252
    for i, panel in enumerate(PANELS):
        px = 16 + (i % 2) * (col_w + 12)
        py = row_y[i // 2]
        draw_panel(cv, px, py, col_w, row_h, panel)
    # Footer ticker.
    cv.fill_rect(0, 976, W, 36, NAVY)
    cv.draw_text_centered(FOOTER, W // 2, 986, 2, WHITE, bold=True)
    return cv


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = encode_png(build())
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())
