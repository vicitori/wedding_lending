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
# Fonts — Cormorant Garamond (elegant serif) + Raleway (light sans)
# ---------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_DIR = os.path.join(_SCRIPT_DIR, "fonts")

pdfmetrics.registerFont(TTFont("Serif",        f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold",    f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-700.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic",  f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Light",   f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-300.ttf"))
pdfmetrics.registerFont(TTFont("Serif-LightIt", f"{_FONT_DIR}/cormorant-garamond-v21-cyrillic_latin-300italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans",          f"{_FONT_DIR}/raleway-v37-cyrillic_latin-300.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Medium",   f"{_FONT_DIR}/raleway-v37-cyrillic_latin-regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Semi",     f"{_FONT_DIR}/raleway-v37-cyrillic_latin-600.ttf"))

# ---------------------------------------------------------
# Palette
# ---------------------------------------------------------
SAGE            = (42 / 255, 58 / 255, 42 / 255)
PAPER           = (252 / 255, 250 / 255, 245 / 255)
CREAM           = (245 / 255, 241 / 255, 233 / 255)
WARM_ZONE       = (246 / 255, 241 / 255, 232 / 255)     # tinted bg for top zone
CHAMPAGNE       = (175 / 255, 145 / 255, 90 / 255)
CHAMPAGNE_LIGHT = (205 / 255, 183 / 255, 142 / 255)
INK             = (48 / 255, 46 / 255, 42 / 255)
INK_LIGHT       = (85 / 255, 82 / 255, 75 / 255)
STONE           = (140 / 255, 133 / 255, 120 / 255)
LINE            = (225 / 255, 218 / 255, 202 / 255)
MIST            = (175 / 255, 190 / 255, 185 / 255)

# ---------------------------------------------------------
# Page geometry
# ---------------------------------------------------------
W, H = A5
MARGIN = 14 * mm
CONTENT_W = W - 2 * MARGIN

BOX_SIZE = 4 * mm
BOX_TEXT_GAP = 6.5 * mm

# Two-column layout
COL_GAP = 6 * mm
LEFT_COL_RIGHT = W * 0.62
RIGHT_COL_LEFT = LEFT_COL_RIGHT + COL_GAP
RIGHT_COL_W = W - MARGIN - RIGHT_COL_LEFT

FOOTER_H = 24 * mm

# ---------------------------------------------------------
# QR
# ---------------------------------------------------------
QR_SVG_PATH = os.path.join(_SCRIPT_DIR, "qr.svg")

c = canvas.Canvas("checklist.pdf", pagesize=A5)

# ---------------------------------------------------------
# Reusable primitives
# ---------------------------------------------------------
def draw_wrapped(x, y, text, width, font="Serif", size=11, leading=4.8 * mm, color=INK):
    c.setFillColorRGB(*color)
    c.setFont(font, size)
    words = text.split()
    line = ""
    yy = y
    for word in words:
        test = (line + " " + word).strip()
        if pdfmetrics.stringWidth(test, font, size) <= width:
            line = test
        else:
            c.drawString(x, yy, line)
            yy -= leading
            line = word
    if line:
        c.drawString(x, yy, line)
    return yy


def checkbox(x, text_baseline_y, text_size=11):
    cap_height = text_size * 0.7
    box_bottom = text_baseline_y + cap_height / 2 - BOX_SIZE / 2
    c.setStrokeColorRGB(*CHAMPAGNE)
    c.setLineWidth(0.6)
    c.rect(x, box_bottom, BOX_SIZE, BOX_SIZE, stroke=1, fill=0)
    return x + BOX_TEXT_GAP


def divider(y, x0=MARGIN, x1=None, color=LINE, width=0.4):
    if x1 is None:
        x1 = W - MARGIN
    c.setStrokeColorRGB(*color)
    c.setLineWidth(width)
    c.line(x0, y, x1, y)


def section(title, y, x=MARGIN, color=CHAMPAGNE):
    c.setFillColorRGB(*color)
    c.setFont("Sans-Semi", 8)
    spaced = "  ".join(title.upper())
    c.drawString(x, y, spaced)


def section_centered(title, y, center_x, color=CHAMPAGNE):
    c.setFillColorRGB(*color)
    c.setFont("Sans-Semi", 8)
    spaced = "  ".join(title.upper())
    c.drawCentredString(center_x, y, spaced)


def draw_background():
    c.setFillColorRGB(*PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_qr_svg(x, y, size):
    drawing = svg2rlg(QR_SVG_PATH)
    sx = size / drawing.width
    sy = size / drawing.height
    drawing.width = size
    drawing.height = size
    drawing.scale(sx, sy)
    renderPDF.draw(drawing, c, x, y)


# ===========================================================
# SINGLE PAGE
# ===========================================================
draw_background()

# ---------- top zone: tinted background for header + checklist ----------
TOP_ZONE_H = 80 * mm
c.setFillColorRGB(*WARM_ZONE)
c.rect(0, H - TOP_ZONE_H, W, TOP_ZONE_H, fill=1, stroke=0)

# ---------- header ----------
y = H - MARGIN

c.setFillColorRGB(*STONE)
c.setFont("Sans-Medium", 8)
c.drawCentredString(W / 2, y, "25 июля  ·  Выборг")
y -= 10 * mm

c.setFillColorRGB(*INK)
c.setFont("Serif-Bold", 26)
c.drawCentredString(W / 2, y, "Путеводитель гостя")
y -= 12 * mm

# ---------- todo checklist (full width) ----------
section("Перед выходом", y)
y -= 6 * mm

todo = [
    "Плотно позавтракать",
    "Приехать к 8:30 на Стачек, 88",
    "Зарядить телефон",
]
for item in todo:
    text_x = checkbox(MARGIN, y, text_size=11)
    c.setFillColorRGB(*INK)
    c.setFont("Serif", 11)
    c.drawString(text_x, y, item)
    y -= 7 * mm

y -= 6 * mm

# ==========================================================
# Two-column zone
# ==========================================================
col_top_y = y

# ---------- LEFT: route timeline ----------
TIMELINE_PADDING = 4 * mm


def timeline_item(y, time, title, text, is_last=False):
    line_x = MARGIN + 5 * mm
    text_x = MARGIN + 16 * mm
    text_w = LEFT_COL_RIGHT - text_x

    # Dot
    c.setFillColorRGB(*CHAMPAGNE)
    c.circle(line_x, y, 1.3 * mm, stroke=0, fill=1)

    # Time
    c.setFillColorRGB(*CHAMPAGNE)
    c.setFont("Sans-Medium", 8.5)
    c.drawString(text_x, y + 0.3 * mm, time)

    # Title
    c.setFillColorRGB(*INK)
    c.setFont("Serif-Bold", 12)
    c.drawString(text_x, y - 4.5 * mm, title)

    # Description — regular weight, readable
    text_bottom = draw_wrapped(text_x, y - 9 * mm, text, text_w,
                               font="Serif", size=10, leading=3.8 * mm,
                               color=INK_LIGHT)
    next_y = text_bottom - TIMELINE_PADDING

    # Connecting line
    if not is_last:
        c.setStrokeColorRGB(*LINE)
        c.setLineWidth(0.5)
        c.line(line_x, y - 1.3 * mm, line_x, next_y + 1.3 * mm)

    return next_y


section("Маршрут дня", col_top_y)
y_left = col_top_y - 7 * mm

route = [
    ("08:30", "Автобус от Автово",
     "Ждём у метро Автово, Стачек 88. Госномер сообщим накануне."),
    ("≈ 10:30", "Парк Монрепо",
     "На входе скажите, что по групповому билету на свадьбу."),
    ("11:00", "Церемония",
     "Регистрация в дворце Монрепо, затем прогулка и фото в парке."),
    ("15:30", "Ресторан",
     "«Птички и ягоды», Приморское шоссе, 572."),
    ("≈ 21:00", "Домой",
     "Выезд из ресторана, приезд к метро Автово около 23:00."),
]
for i, (time_label, title, text) in enumerate(route):
    is_last = i == len(route) - 1
    y_left = timeline_item(y_left, time_label, title, text, is_last=is_last)

# ---------- Vertical divider between columns ----------
col_divider_x = LEFT_COL_RIGHT + COL_GAP / 2
c.setStrokeColorRGB(*LINE)
c.setLineWidth(0.4)
c.line(col_divider_x, col_top_y + 3 * mm,
       col_divider_x, FOOTER_H + 6 * mm)

# ---------- RIGHT: QR block ----------
right_center_x = (col_divider_x + W - MARGIN) / 2

section_centered("Фотографии", col_top_y, right_center_x)
y_right = col_top_y - 7 * mm

c.setFillColorRGB(*INK_LIGHT)
c.setFont("Serif-Italic", 10)
c.drawCentredString(right_center_x, y_right, "Присылайте фотографии")
y_right -= 4.5 * mm
c.drawCentredString(right_center_x, y_right, "с торжества")
y_right -= 7 * mm

QR_SIZE = 26 * mm
qr_x = right_center_x - QR_SIZE / 2
qr_y = y_right - QR_SIZE

QR_FRAME_PAD = 1.5 * mm
c.setStrokeColorRGB(*CHAMPAGNE)
c.setLineWidth(0.4)
c.rect(qr_x - QR_FRAME_PAD, qr_y - QR_FRAME_PAD,
       QR_SIZE + 2 * QR_FRAME_PAD, QR_SIZE + 2 * QR_FRAME_PAD,
       stroke=1, fill=0)

draw_qr_svg(qr_x, qr_y, QR_SIZE)

# ---------- footer ----------
c.setFillColorRGB(*SAGE)
c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)

footer_cx = W / 2
footer_mid = FOOTER_H / 2

c.setFillColorRGB(*CHAMPAGNE_LIGHT)
c.setFont("Sans", 7.5)
c.drawCentredString(footer_cx, footer_mid + 6 * mm, "ЕСЛИ  ПОТЕРЯЕТЕСЬ")

c.setFillColorRGB(*CREAM)
c.setFont("Serif-Bold", 13)
c.drawCentredString(footer_cx, footer_mid, "Кирилл")

c.setFillColorRGB(*CREAM)
c.setFont("Serif", 10.5)
c.drawCentredString(footer_cx, footer_mid - 5.5 * mm,
                    "+7 910 966 6402  ·  телеграм @tepa46")

# ---------------------------------------------------------
c.showPage()
c.save()
print("done")
