"""Generate art-directed material studies for the portfolio covers.

No stock photography: each plate is a procedural render of a dark material,
light study or structural grid, tone mapped into the site palette.
"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os

W, H = 1500, 1875
OUT = os.path.join(os.path.dirname(__file__), "..", "dist", "assets", "img")
os.makedirs(OUT, exist_ok=True)

rng_global = np.random.default_rng(7)


def noise(w, h, scale, seed):
    rng = np.random.default_rng(seed)
    gw = max(2, int(w / scale))
    gh = max(2, int(h / scale))
    grid = (rng.random((gh, gw)) * 255).astype(np.uint8)
    img = Image.fromarray(grid, "L").resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def fbm(w, h, seed, octaves=4, base=220, persistence=0.55):
    out = np.zeros((h, w), np.float32)
    amp, total, scale = 1.0, 0.0, base
    for i in range(octaves):
        out += noise(w, h, scale, seed + i * 13) * amp
        total += amp
        amp *= persistence
        scale /= 2.0
    return out / total


def grid_xy():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    return x / W, y / H


def tone(lum, shadow, highlight, gamma=1.0):
    t = np.clip(lum, 0, 1) ** gamma
    s = np.array(shadow, np.float32) / 255.0
    hi = np.array(highlight, np.float32) / 255.0
    img = s[None, None, :] * (1 - t[..., None]) + hi[None, None, :] * t[..., None]
    return img


def finish(img, grain=0.012, vignette=0.55, seed=1, warm_glow=None, glow_strength=0.0, exposure=1.0):
    x, y = grid_xy()
    rng = np.random.default_rng(seed)
    # vignette
    dx, dy = (x - 0.5) * 1.1, (y - 0.5) * 1.1
    r = np.sqrt(dx * dx + dy * dy) / 0.78
    img *= (1 - vignette * np.clip(r, 0, 1) ** 1.7)[..., None]
    if warm_glow is not None and glow_strength > 0:
        gx, gy, gr = warm_glow
        d2 = ((x - gx) ** 2) * (W / H) + ((y - gy) ** 2)
        g = np.exp(-d2 / (2 * gr * gr))[..., None]
        img += np.array([1.0, 0.34, 0.09], np.float32)[None, None, :] * g * glow_strength
    img *= exposure
    img += rng.normal(0, grain, (H, W, 1)).astype(np.float32)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")


def structure_mask(draw_fn, blur=1.4):
    m = Image.new("L", (W, H), 0)
    draw_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, dtype=np.float32) / 255.0


def save(img, name, quality=82):
    img.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=quality, method=6)
    print(name, os.path.getsize(os.path.join(OUT, name + ".webp")) // 1024, "KB")


# ---------------------------------------------------------------------------
# 1. framework ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â architectural slats, hard light through a gap
# ---------------------------------------------------------------------------
def framework():
    x, y = grid_xy()
    n = fbm(W, H, 101, octaves=5, base=260)
    slats = 0.5 + 0.5 * np.sin(x * 44 + (n - 0.5) * 2.4)
    wide = 0.5 + 0.5 * np.sin(x * 9 + (n - 0.5) * 1.2)
    lum = 0.16 + slats * 0.10 + wide * 0.10 + n * 0.12
    # bright vertical gap
    gap = np.exp(-((x - 0.665) ** 2) / (2 * 0.045 ** 2))
    lum += gap * (0.45 + 0.35 * np.clip(1 - y, 0, 1))
    # floor light
    lum += np.clip((y - 0.72) / 0.28, 0, 1) * 0.12
    img = finish(tone(lum, (8, 8, 7), (198, 190, 176), 1.05), grain=0.014, vignette=0.5,
                 seed=2, warm_glow=(0.66, 0.30, 0.34), glow_strength=0.045)
    save(img, "framework")


# ---------------------------------------------------------------------------
# 2. atelier ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â soft haze, folded light
# ---------------------------------------------------------------------------
def atelier():
    x, y = grid_xy()
    dx, dy = (x + 0.25) * (W / H), (y - 0.28)
    r = np.sqrt(dx * dx + dy * dy)
    n = fbm(W, H, 202, octaves=4, base=150)
    # curved wall with a hard light terminator
    curves = 0.5 + 0.5 * np.sin(r * 46 + n * 1.6)
    terminator = np.clip((0.62 - r) / 0.5, 0, 1) ** 1.6
    lum = 0.06 + curves * 0.20 * terminator + n * 0.04
    # sharp vertical edge light
    edge = np.exp(-((x - 0.74) ** 2) / (2 * 0.006 ** 2))
    lum += edge * (0.45 + 0.25 * n)
    lum += np.exp(-(((x - 0.74) ** 2) / 0.006)) * 0.10
    img = finish(tone(lum, (8, 8, 7), (218, 206, 184), 1.02), grain=0.012, vignette=0.66,
                 seed=3, warm_glow=(0.72, 0.4, 0.26), glow_strength=0.05)
    save(img, "atelier")


# ---------------------------------------------------------------------------
# 3. steel ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â brushed metal, oil sheen
# ---------------------------------------------------------------------------
def steel():
    x, y = grid_xy()
    brush = noise(W, H, 1.6, 311)
    brush2 = noise(W, H, 3.4, 313)
    brush3 = noise(W, H, 22, 317)
    # hard specular sweep across brushed metal
    band = np.exp(-((y - 0.34 - (x - 0.5) * 0.18) ** 2) / (2 * 0.035 ** 2))
    band2 = np.exp(-((y - 0.66) ** 2) / (2 * 0.012 ** 2))
    lum = 0.09 + 0.10 * brush + 0.05 * brush2 + 0.14 * band + 0.30 * band2
    lum += 0.05 * (0.5 + 0.5 * np.sin(x * 160 + brush3 * 2))
    lum += np.clip((0.9 - x), 0, 1) * 0.03
    img = finish(tone(lum, (7, 8, 8), (210, 208, 200), 1.0), grain=0.008, vignette=0.6,
                 seed=4, warm_glow=(0.3, 0.66, 0.2), glow_strength=0.04, exposure=0.98)
    save(img, "steel")


# ---------------------------------------------------------------------------
# 4. machinery ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â concentric machined rings
# ---------------------------------------------------------------------------
def machinery():
    x, y = grid_xy()
    cx, cy = 0.54, 0.47
    dx, dy = (x - cx) * (W / H), (y - cy)
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    n = fbm(W, H, 404, octaves=4, base=420)
    rings = 0.5 + 0.5 * np.sin(r * 230 + n * 1.4)
    sharp = rings ** 5
    falloff = np.exp(-r * 1.9)
    spokes = (0.5 + 0.5 * np.sin(ang * 60)) * 0.10
    lum = 0.05 + 0.07 * n + sharp * 0.62 * falloff + spokes * falloff
    lum += np.exp(-((r - 0.035) ** 2) / (2 * 0.012 ** 2)) * 0.35
    lum += np.exp(-(r ** 2) / 0.002) * 0.25
    img = finish(tone(lum, (6, 7, 8), (214, 208, 196), 1.0), grain=0.009, vignette=0.5,
                 seed=5, warm_glow=(0.54, 0.47, 0.22), glow_strength=0.05)
    save(img, "machinery")


# ---------------------------------------------------------------------------
# 5. facade ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â perspective grid, night elevation
# ---------------------------------------------------------------------------
def facade():
    x, y = grid_xy()
    cx, horizon = 0.60, 0.42

    def draw(d):
        for i in range(-8, 22):
            d.line([(cx * W, horizon * H), (i * W / 10, H * 1.25)], fill=190, width=2)
        for j in range(1, 16):
            yy = horizon * H + (H - horizon * H) * (j / 15.0) ** 1.9
            d.line([(0, yy), (W, yy)], fill=120, width=2)
        for j in range(1, 9):
            yy = horizon * H * (1 - (j / 9.0) ** 1.7)
            d.line([(0, yy), (W, yy)], fill=70, width=1)

    lines = structure_mask(draw, blur=1.1)
    n = fbm(W, H, 505, octaves=4, base=200)
    lum = 0.09 + 0.05 * n + lines * 0.16
    glow = np.exp(-(((x - 0.58) ** 2) / 0.10 + ((y - 0.44) ** 2) / 0.03))
    lum += glow * 0.28
    lum += np.clip((y - 0.55) / 0.45, 0, 1) * 0.04
    img = finish(tone(lum, (7, 7, 8), (188, 180, 168), 1.0), grain=0.012, vignette=0.6,
                 seed=6, warm_glow=(0.58, 0.44, 0.22), glow_strength=0.07)
    save(img, "facade")


# ---------------------------------------------------------------------------
# 6. stockroom ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â racking silhouettes, deep aisle
# ---------------------------------------------------------------------------
def stockroom():
    x, y = grid_xy()
    cx, horizon = 0.50, 0.34

    def draw(d):
        for i in range(-4, 14):
            d.line([(cx * W, horizon * H), (i * W / 8, H * 1.15)], fill=200, width=3)
        for i in range(-3, 11):
            d.line([(cx * W, horizon * H), ((i + 0.35) * W / 8, H * 1.0)], fill=90, width=1)
        for j in range(1, 11):
            yy = horizon * H + (H - horizon * H) * (j / 10.0) ** 2.1
            d.line([(0, yy), (W, yy)], fill=150, width=3)
        # pallet blocks
        for i in range(6):
            for j in range(5):
                yy = horizon * H + (H - horizon * H) * ((j + 0.4) / 6.0) ** 2.0
                half = (yy / H) ** 1.5 * W * 0.16
                cx_i = W * (0.5 + (i - 2.5) * (0.16 + (yy / H) * 0.1))
                d.rectangle([cx_i - half * 0.5, yy - half * 0.22, cx_i + half * 0.5, yy + half * 0.18], fill=55)

    lines = structure_mask(draw, blur=2.2)
    n = fbm(W, H, 606, octaves=4, base=180)
    lum = 0.06 + 0.10 * n + lines * 0.34
    lum += np.exp(-((x - 0.5) ** 2) / 0.02) * np.clip(1 - y / 0.8, 0, 1) * 0.12
    img = finish(tone(lum, (6, 6, 6), (188, 178, 162), 1.0), grain=0.015, vignette=0.7,
                 seed=7, warm_glow=(0.5, 0.33, 0.26), glow_strength=0.06)
    save(img, "stockroom")


# ---------------------------------------------------------------------------
# 7. archive ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â stacked strata, letterpress paper
# ---------------------------------------------------------------------------
def archive():
    x, y = grid_xy()
    n1 = fbm(W, H, 707, octaves=5, base=300)
    n2 = noise(W, H, 4, 711)
    strata = 0.5 + 0.5 * np.sin(y * 90 + n1 * 7.0)
    lum = 0.10 + 0.20 * n1 + 0.10 * strata + 0.03 * n2
    # horizontal sheet edges
    edges = (np.abs(np.sin(y * 46 + n1 * 3.0)) ** 30)
    lum += edges * 0.22
    lum += np.exp(-(((x - 0.5) ** 2) / 0.16 + ((y - 0.5) ** 2) / 0.28)) * 0.16
    img = finish(tone(lum, (10, 9, 7), (206, 194, 170), 1.05), grain=0.02, vignette=0.55,
                 seed=8, warm_glow=(0.7, 0.6, 0.3), glow_strength=0.03)
    save(img, "archive")


# ---------------------------------------------------------------------------
# 8. signal ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â a single beam in fog
# ---------------------------------------------------------------------------
def signal():
    x, y = grid_xy()
    n = fbm(W, H, 808, octaves=5, base=240)
    fog = fbm(W, H, 818, octaves=4, base=120)
    # diagonal beam
    d = np.abs((x - 0.18) * 0.72 - (y - 0.08) * 0.7)
    beam = np.exp(-(d ** 2) / (2 * 0.012 ** 2))
    beam += np.exp(-(d ** 2) / (2 * 0.08 ** 2)) * 0.28
    lum = 0.07 + 0.08 * fog + beam * 0.55 * (0.55 + 0.45 * n)
    lum += np.exp(-(((x - 0.2) ** 2) / 0.10 + ((y - 0.1) ** 2) / 0.06)) * 0.12
    img = finish(tone(lum, (6, 6, 7), (232, 222, 204), 1.0), grain=0.018, vignette=0.62,
                 seed=9, warm_glow=(0.2, 0.1, 0.25), glow_strength=0.1, exposure=0.96)
    save(img, "signal")


# ---------------------------------------------------------------------------
# 9. granite ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â polished stone
# ---------------------------------------------------------------------------
def granite():
    x, y = grid_xy()
    fine = noise(W, H, 2.0, 909)
    mid = noise(W, H, 9, 919)
    large = fbm(W, H, 929, octaves=5, base=260)
    speck = (fine > 0.72).astype(np.float32) * 0.6 + (fine < 0.2).astype(np.float32) * 0.25
    lum = 0.10 + 0.10 * large + 0.06 * mid + speck * 0.22
    vein = np.exp(-((np.sin((x * 4 + y * 3 + large * 8) * 3.1415)) ** 2) / 0.02)
    lum += vein * 0.10
    lum += np.exp(-(((x - 0.3) ** 2) / 0.3 + ((y - 0.2) ** 2) / 0.4)) * 0.10
    img = finish(tone(lum, (9, 9, 8), (198, 192, 180), 1.0), grain=0.012, vignette=0.55,
                 seed=10, warm_glow=(0.35, 0.25, 0.3), glow_strength=0.025)
    save(img, "granite")


# ---------------------------------------------------------------------------
# 10. terminal ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â screen light, scan lines
# ---------------------------------------------------------------------------
def terminal():
    x, y = grid_xy()

    def draw(d):
        for i in range(0, 26):
            d.line([(i * W / 25, 0), (i * W / 25, H)], fill=120, width=1)
        for j in range(0, 40):
            d.line([(0, j * H / 39), (W, j * H / 39)], fill=70, width=1)
        # a few lit cells
        for (i, j) in [(6, 24), (7, 24), (8, 24), (12, 25), (13, 25), (18, 23), (19, 23), (19, 22)]:
            d.rectangle([i * W / 25 + 3, j * H / 39 + 3, (i + 1) * W / 25 - 3, (j + 1) * H / 39 - 3], fill=255)

    grid = structure_mask(draw, blur=0.7)
    n = fbm(W, H, 111, octaves=3, base=340)
    lum = 0.08 + grid * 0.42 + n * 0.05
    band = np.exp(-((y - 0.64) ** 2) / (2 * 0.09 ** 2))
    lum += band * 0.26 * grid
    lum += np.exp(-(((x - 0.7) ** 2) / 0.10 + ((y - 0.64) ** 2) / 0.16)) * 0.12
    lum += np.clip((y - 0.88) / 0.12, 0, 1) * 0.05
    img = finish(tone(lum, (6, 8, 9), (196, 202, 204), 1.0), grain=0.012, vignette=0.62,
                 seed=11, warm_glow=(0.68, 0.62, 0.22), glow_strength=0.06, exposure=1.0)
    save(img, "terminal")


# ---------------------------------------------------------------------------
# hero and project photographs are generated separately (see tools/generated)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    framework()
    atelier()
    stockroom()
    archive()
    signal()
    granite()
    terminal()
    print("done")
