# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import os

# ---------------------------------------------------------
# Fonts — 4 styles only
# ---------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_DIR = os.path.join(_SCRIPT_DIR, "fonts")

pdfmetrics.registerFont(TTFont("Serif",       f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold",   f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-700.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{_FONT_DIR}/raleway-v37-cyrillic_latin-600.ttf"))

# ---------------------------------------------------------
# Palette — 8 purposeful colors, no extras
# ---------------------------------------------------------
SAGE  = (42 / 255, 58 / 255, 42 / 255)
PAPER = (252 / 255, 250 / 255, 245 / 255)
WARM  = (242 / 255, 237 / 255, 227 / 255)
CREAM = (245 / 255, 241 / 255, 233 / 255)
GOLD  = (175 / 255, 145 / 255, 90 / 255)
INK   = (48 / 255, 46 / 255, 42 / 255)
SOFT  = (105 / 255, 100 / 255, 90 / 255)
LINE  = (218 / 255, 212 / 255, 198 / 255)

# ---------------------------------------------------------
# Grid — every vertical spacing is a multiple of S
# ---------------------------------------------------------
W, H = A5
MARGIN = 14 * mm
S = 4 * mm

FOOTER_H = 7 * S       # 28mm
TOP_ZONE_H = 18 * S    # 72mm
QR_SIZE = 5 * S         # 20mm

QR_SVG_PATH = os.path.join(_SCRIPT_DIR, "qr.svg")
c = canvas.Canvas("checklist.pdf", pagesize=A5)


def draw_qr_svg(x, y, size):
    d = svg2rlg(QR_SVG_PATH)
    sx, sy = size / d.width, size / d.height
    d.width = d.height = size
    d.scale(sx, sy)
    renderPDF.draw(d, c, x, y)


# ==========================================================
# PAGE
# ==========================================================

# Background
c.setFillColorRGB(*PAPER)
c.rect(0, 0, W, H, fill=1, stroke=0)

# Top zone — warm tint
c.setFillColorRGB(*WARM)
c.rect(0, H - TOP_ZONE_H, W, TOP_ZONE_H, fill=1, stroke=0)

# Bottom zone — warm tint for QR area
BOTTOM_ZONE_H = 7 * S   # 28mm from footer top
c.setFillColorRGB(*WARM)
c.rect(0, FOOTER_H, W, BOTTOM_ZONE_H, fill=1, stroke=0)

# ---------- Header ----------
y = H - 3 * S

c.setFillColorRGB(*SOFT)
c.setFont("Sans", 8)
c.drawCentredString(W / 2, y, "25 ИЮЛЯ · ВЫБОРГ")

y -= 3 * S

c.setFillColorRGB(*INK)
c.setFont("Serif-Bold", 28)
c.drawCentredString(W / 2, y, "Памятка гостя")

y -= 4 * S

# ---------- Checklist ----------
# Shared axis for timeline dots, checkboxes, QR
DOT_X = MARGIN + S
TEXT_X = MARGIN + 3 * S

c.setFillColorRGB(*GOLD)
c.setFont("Sans", 8)
c.drawString(TEXT_X, y, "ПЕРЕД ВЫХОДОМ")

y -= 2 * S

for item in ["Плотно позавтракать",
             "Приехать к 8:30 на Стачек, 88",
             "Зарядить телефон"]:
    # Box centered on DOT_X axis
    box_y = y - 0.5 * mm
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.6)
    c.rect(DOT_X - S / 2, box_y, S, S, stroke=1, fill=0)

    c.setFillColorRGB(*INK)
    c.setFont("Serif", 12)
    c.drawString(TEXT_X, y, item)
    y -= 2 * S

y -= 2 * S

# ---------- Timeline ----------
c.setFillColorRGB(*GOLD)
c.setFont("Sans", 8)
c.drawString(TEXT_X, y, "МАРШРУТ ДНЯ")

y -= 2 * S

route = [
    ("08:30",   "Автобус от Автово, Стачек 88"),
    ("11:00",   "Приезжаем в Монрепо"),
    ("12:00",   "Регистрация"),
    ("15:30",   "Начало банкета"),
    ("~21:00",  "Выезжаем домой, приезд ~23:00"),
]

for i, (time, title) in enumerate(route):
    is_last = (i == len(route) - 1)

    # Dot — vertically centered on time text (~cap height / 2)
    dot_cy = y + 1 * mm
    c.setFillColorRGB(*GOLD)
    c.circle(DOT_X, dot_cy, 1.6 * mm, stroke=0, fill=1)

    # Time — large, prominent
    c.setFillColorRGB(*INK)
    c.setFont("Sans", 12)
    c.drawString(TEXT_X, y, time)

    # Title — below time, softer
    c.setFillColorRGB(*SOFT)
    c.setFont("Serif", 11)
    c.drawString(TEXT_X, y - 5 * mm, title)

    next_y = y - 3 * S

    # Connecting line — from bottom of dot to top of next dot
    if not is_last:
        next_dot_cy = next_y + 1 * mm
        c.setStrokeColorRGB(*LINE)
        c.setLineWidth(0.5)
        c.line(DOT_X, dot_cy - 1.6 * mm, DOT_X, next_dot_cy + 1.6 * mm)

    y = next_y

y -= 2 * S

# QR + label centered in content area (y to FOOTER_H)
CAP_AND_DESC = 4 * mm
total_block = QR_SIZE + S + CAP_AND_DESC
block_top = (y + FOOTER_H) / 2 + total_block / 2
block_top = min(block_top, y)  # don't exceed content top

qr_x = W / 2 - QR_SIZE / 2
qr_y = block_top - QR_SIZE

draw_qr_svg(qr_x, qr_y, QR_SIZE)

c.setFillColorRGB(*SAGE)
c.setFont("Serif-Italic", 10)
c.drawCentredString(W / 2, qr_y - 3 * mm, "присылайте фотографии с торжества")

# ---------- Footer ----------
c.setFillColorRGB(*SAGE)
c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)

mid = FOOTER_H / 2

c.setFillColorRGB(*CREAM)
c.setFont("Serif-Bold", 14)
c.drawCentredString(W / 2, mid + S, "Свидетель Кирилл")

c.setFont("Serif", 11)
c.drawCentredString(W / 2, mid - S,
                    "+7 910 966 6402  ·  телеграм @tepa46")

# ----------
c.showPage()
c.save()
print("done")
