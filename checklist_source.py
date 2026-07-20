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
# Fonts
# ---------------------------------------------------------
_FONT_DIR = "/Library/Fonts"
pdfmetrics.registerFont(TTFont("Serif", f"{_FONT_DIR}/DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", f"{_FONT_DIR}/DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", f"{_FONT_DIR}/DejaVuSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Mono", f"{_FONT_DIR}/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold", f"{_FONT_DIR}/DejaVuSansMono-Bold.ttf"))

# ---------------------------------------------------------
# Palette
# ---------------------------------------------------------
PINE = (24 / 255, 34 / 255, 25 / 255)
PAPER = (251 / 255, 248 / 255, 241 / 255)
PARCHMENT = (243 / 255, 238 / 255, 227 / 255)
GOLD = (169 / 255, 130 / 255, 79 / 255)
GOLD_LIGHT = (199 / 255, 168 / 255, 118 / 255)
INK = (36 / 255, 36 / 255, 32 / 255)
STONE = (140 / 255, 133 / 255, 112 / 255)
LINE = (222 / 255, 210 / 255, 184 / 255)
MIST = (183 / 255, 196 / 255, 196 / 255)

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

FOOTER_H = 30 * mm

# ---------------------------------------------------------
# QR-код (SVG-файл рядом со скриптом)
# ---------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QR_SVG_PATH = os.path.join(_SCRIPT_DIR, "qr.svg")

c = canvas.Canvas("checklist.pdf", pagesize=A5)

# ---------------------------------------------------------
# Reusable primitives
# ---------------------------------------------------------
def draw_wrapped(x, y, text, width, font="Serif", size=9.4, leading=4.6 * mm, color=INK):
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


def checkbox(x, text_baseline_y, text_size=9.8):
    cap_height = text_size * 0.7
    box_bottom = text_baseline_y + cap_height / 2 - BOX_SIZE / 2
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.8)
    c.rect(x, box_bottom, BOX_SIZE, BOX_SIZE, stroke=1, fill=0)
    return x + BOX_TEXT_GAP


def divider(y, x0=MARGIN, x1=None, color=LINE, width=0.55):
    if x1 is None:
        x1 = W - MARGIN
    c.setStrokeColorRGB(*color)
    c.setLineWidth(width)
    c.line(x0, y, x1, y)


def section(title, y, x=MARGIN, color=GOLD):
    c.setFillColorRGB(*color)
    c.setFont("Mono-Bold", 8.5)
    c.drawString(x, y, title.upper())


def draw_background():
    c.setFillColorRGB(*PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_qr_svg(x, y, size):
    """Рисует QR-код из qr.svg с левого-нижнего угла (x, y), сторона size."""
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

# ---------- header ----------
HEADER_H = 26 * mm
c.setFillColorRGB(*PINE)
c.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)

c.setFillColorRGB(*GOLD_LIGHT)
c.setFont("Mono", 7)
c.drawString(MARGIN, H - 9 * mm, "25 ИЮЛЯ · ВЫБОРГ · СВАДЕБНЫЙ ЧЕК-ЛИСТ")

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Bold", 20)
c.drawString(MARGIN, H - 19.5 * mm, "Путеводитель гостя")

y = H - HEADER_H - 7 * mm

# ---------- todo checklist (full width) ----------
section("Перед выходом", y)
y -= 6 * mm

todo = [
    "Плотно позавтракать",
    "Приехать к 8:30 на Стачек, 88",
    "Зарядить телефон",
]
for item in todo:
    text_x = checkbox(MARGIN, y, text_size=9.8)
    c.setFillColorRGB(*INK)
    c.setFont("Serif", 9.8)
    c.drawString(text_x, y, item)
    y -= 7 * mm

y += 1.5 * mm
divider(y, x1=LEFT_COL_RIGHT)
y -= 8 * mm

# ==========================================================
# Two-column zone: route (left) + QR (right)
# ==========================================================
col_top_y = y

# ---------- LEFT: route timeline ----------
TIMELINE_PADDING = 5 * mm


def timeline_item(y, time, title, text, is_last=False):
    line_x = MARGIN + 5 * mm
    text_x = MARGIN + 16 * mm
    text_w = LEFT_COL_RIGHT - text_x

    # Dot
    c.setFillColorRGB(*GOLD)
    c.circle(line_x, y, 1.4 * mm, stroke=0, fill=1)

    # Time
    c.setFillColorRGB(*GOLD)
    c.setFont("Mono-Bold", 8)
    c.drawString(text_x, y + 0.3 * mm, time)

    # Title
    c.setFillColorRGB(*PINE)
    c.setFont("Serif-Bold", 10.5)
    c.drawString(text_x, y - 4.2 * mm, title)

    # Description — dynamic height
    text_bottom = draw_wrapped(text_x, y - 8.5 * mm, text, text_w,
                               size=8.2, leading=3.6 * mm)
    next_y = text_bottom - TIMELINE_PADDING

    # Connecting line to next item
    if not is_last:
        c.setStrokeColorRGB(*LINE)
        c.setLineWidth(0.6)
        c.line(line_x, y - 1.4 * mm, line_x, next_y + 1.4 * mm)

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
c.setLineWidth(0.5)
c.line(col_divider_x, col_top_y + 3 * mm,
       col_divider_x, FOOTER_H + 4 * mm)

# ---------- RIGHT: QR block ----------
# Visual center between divider line and right margin
right_center_x = (col_divider_x + W - MARGIN) / 2

c.setFillColorRGB(*GOLD)
c.setFont("Mono-Bold", 8.5)
c.drawCentredString(right_center_x, col_top_y, "ФОТОГРАФИИ")
y_right = col_top_y - 6 * mm

c.setFillColorRGB(*INK)
c.setFont("Serif-Italic", 8.2)
c.drawCentredString(right_center_x, y_right, "Присылайте фотографии")
y_right -= 4 * mm
c.drawCentredString(right_center_x, y_right, "с торжества")
y_right -= 6 * mm

QR_SIZE = 26 * mm
qr_x = right_center_x - QR_SIZE / 2
qr_y = y_right - QR_SIZE

QR_FRAME_PAD = 1.5 * mm
c.setStrokeColorRGB(*GOLD)
c.setLineWidth(0.5)
c.rect(qr_x - QR_FRAME_PAD, qr_y - QR_FRAME_PAD,
       QR_SIZE + 2 * QR_FRAME_PAD, QR_SIZE + 2 * QR_FRAME_PAD,
       stroke=1, fill=0)

draw_qr_svg(qr_x, qr_y, QR_SIZE)

# ---------- footer / contacts ----------
c.setFillColorRGB(*PINE)
c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)

# Footer geometry: two zones split at page center
footer_div_x = W / 2
FOOTER_PAD = 5 * mm
FOOTER_LINE_H = 5.5 * mm
# 4 lines vertically centered: top = center + 1.5 * spacing
footer_line_top = FOOTER_H / 2 + 1.5 * FOOTER_LINE_H

# Left zone: contacts (left-aligned to MARGIN)
c.setFillColorRGB(*GOLD_LIGHT)
c.setFont("Mono", 7)
c.drawString(MARGIN, footer_line_top, "ЕСЛИ ПОТЕРЯЕТЕСЬ")

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Bold", 13)
c.drawString(MARGIN, footer_line_top - FOOTER_LINE_H, "Кирилл")

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif", 10)
c.drawString(MARGIN, footer_line_top - 2 * FOOTER_LINE_H, "+7 910 966 6402")

c.setFillColorRGB(*MIST)
c.setFont("Mono", 7.5)
c.drawString(MARGIN, footer_line_top - 3 * FOOTER_LINE_H, "@tepa46")

# Divider (centered)
c.setStrokeColorRGB(*GOLD)
c.setLineWidth(0.4)
c.line(footer_div_x, FOOTER_PAD, footer_div_x, FOOTER_H - FOOTER_PAD)

# Right zone: message (centered in its half)
right_msg_center = (footer_div_x + W - MARGIN) / 2

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Italic", 9.5)
c.drawCentredString(right_msg_center, footer_line_top, "Очень ждём")
c.drawCentredString(right_msg_center, footer_line_top - FOOTER_LINE_H, "этого дня")
c.drawCentredString(right_msg_center, footer_line_top - 2 * FOOTER_LINE_H, "и встречи")
c.drawCentredString(right_msg_center, footer_line_top - 3 * FOOTER_LINE_H, "с вами!")

# ---------------------------------------------------------
c.showPage()
c.save()
print("done")
