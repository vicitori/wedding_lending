# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

# ---------------------------------------------------------
# Fonts
# ---------------------------------------------------------

pdfmetrics.registerFont(
    TTFont("Serif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
)
pdfmetrics.registerFont(
    TTFont("Serif-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
)
pdfmetrics.registerFont(
    TTFont("Serif-Italic", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf")
)
pdfmetrics.registerFont(
    TTFont("Mono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
)
pdfmetrics.registerFont(
    TTFont("Mono-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
)

# ---------------------------------------------------------
# Palette (совпадает с переменными сайта)
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

c = canvas.Canvas("/home/claude/checklist.pdf", pagesize=A5)

# ---------------------------------------------------------
# Reusable primitives
# ---------------------------------------------------------


def draw_wrapped(x, y, text, width, font="Serif", size=9.4, leading=4.6 * mm, color=INK):
    """Draws left-aligned wrapped text, returns the y of the last line drawn."""
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


def checkbox(x, y):
    c.setStrokeColorRGB(*GOLD)
    c.setLineWidth(0.8)
    s = 4 * mm
    c.rect(x, y - s + 0.6 * mm, s, s, stroke=1, fill=0)


def divider(y, x0=MARGIN, x1=None, color=LINE, width=0.55):
    if x1 is None:
        x1 = W - MARGIN
    c.setStrokeColorRGB(*color)
    c.setLineWidth(width)
    c.line(x0, y, x1, y)


def section(title, y, color=GOLD):
    c.setFillColorRGB(*color)
    c.setFont("Mono-Bold", 8.5)
    c.drawString(MARGIN, y, title.upper())


def draw_background():
    c.setFillColorRGB(*PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def new_page():
    c.showPage()
    draw_background()


# ===========================================================
# PAGE 1 — чек-лист "не забыть" + маршрут дня
# ===========================================================

draw_background()

# ---------- header ----------
HEADER_H = 44 * mm
c.setFillColorRGB(*PINE)
c.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)

c.setFillColorRGB(*GOLD_LIGHT)
c.setFont("Mono", 7.3)
c.drawString(MARGIN, H - 10 * mm, "25 ИЮЛЯ · ВЫБОРГ · СВАДЕБНЫЙ ЧЕК-ЛИСТ")

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Bold", 22)
c.drawString(MARGIN, H - 20 * mm, "Путеводитель гостя")

c.setFillColorRGB(*MIST)
c.setFont("Serif-Italic", 9.3)
c.drawString(MARGIN, H - 28 * mm, "Приехать вовремя — самая сложная задача.")
c.drawString(MARGIN, H - 33 * mm, "Дальше будет только приятное.")

y = H - HEADER_H - 9 * mm

# ---------- todo checklist ----------
section("Перед выходом", y)
y -= 7 * mm

todo = [
    "Плотно позавтракать",
    "Приехать к 8:30",
    "Зарядить телефон",
    "Не брать цветы из города",
]

for item in todo:
    checkbox(MARGIN, y + 1.2 * mm)
    c.setFillColorRGB(*INK)
    c.setFont("Serif", 9.8)
    c.drawString(MARGIN + 7 * mm, y, item)
    y -= 6.8 * mm

y += 0.8 * mm
divider(y)
y -= 9 * mm

# ---------- route timeline ----------


def timeline_item(y, time, title, text, is_last=False):
    line_x = MARGIN + 5 * mm
    text_x = MARGIN + 24 * mm
    text_w = CONTENT_W - 25 * mm

    if not is_last:
        c.setStrokeColorRGB(*LINE)
        c.setLineWidth(0.7)
        c.line(line_x, y + 1.5 * mm, line_x, y - 14.5 * mm)

    c.setFillColorRGB(*GOLD)
    c.circle(line_x, y, 1.6 * mm, stroke=0, fill=1)

    c.setFillColorRGB(*GOLD)
    c.setFont("Mono-Bold", 8.6)
    c.drawString(text_x, y + 0.3 * mm, time)

    c.setFillColorRGB(*PINE)
    c.setFont("Serif-Bold", 11.3)
    c.drawString(text_x, y - 4.6 * mm, title)

    draw_wrapped(text_x, y - 9.2 * mm, text, text_w, size=8.7, leading=3.9 * mm)

    return y - 17.5 * mm


section("Маршрут дня", y)
y -= 8 * mm

route = [
    ("08:30", "Автобус",
     "Yutong ждёт у метро Автово. Точка сбора — Стачек, 88. Ждём не дольше 5–10 минут."),
    ("≈ 11:00", "Монрепо",
     "На входе скажите, что вы по групповому билету. По дороге — остановка, в автобусе есть вода."),
    ("после церемонии", "Прогулка",
     "Гуляем по парку и фотографируемся — фотограф работает только здесь."),
    ("15:30", "Ресторан",
     "«Птички и ягоды». Очень просим хорошо позавтракать утром."),
    ("≈ 23:00", "Домой",
     "Возвращаемся тем же автобусом к метро Автово."),
]

for i, (time_label, title, text) in enumerate(route):
    is_last = i == len(route) - 1
    y = timeline_item(y, time_label, title, text, is_last=is_last)

# ===========================================================
# PAGE 2 — важно / дресс-код / контакты
# ===========================================================

new_page()
y = H - 16 * mm
FOOTER_H = 34 * mm

# ---------- important cards (2x2) ----------
section("Важно помнить", y)
y -= 9 * mm

left = MARGIN
right = W / 2 + 2 * mm
card_w = W / 2 - MARGIN - 4 * mm

cards = [
    ("Позавтракайте", "Первый полноценный приём пищи будет только около 15:30.", left),
    ("Вода будет", "В автобусе есть питьевая вода, по дороге будет остановка.", right),
    ("Цветы не нужны", "Не везите их из города — дорога будет долгой.", left),
    ("Фотограф", "Красивые фотографии постараемся сделать именно в Монрепо.", right),
]

row1_y = y
row2_y = y - 24 * mm

for i, (title, text, x) in enumerate(cards):
    row_y = row1_y if i < 2 else row2_y
    checkbox(x, row_y + 1 * mm)
    c.setFillColorRGB(*INK)
    c.setFont("Serif-Bold", 10)
    c.drawString(x + 6.5 * mm, row_y, title)
    draw_wrapped(x + 6.5 * mm, row_y - 4.6 * mm, text, card_w, size=8.4, leading=3.7 * mm)

y = row2_y - 18 * mm
divider(y)
y -= 10 * mm

# ---------- dress code ----------
section("Дресс-код", y)
y -= 9 * mm

c.setFillColorRGB(*INK)
c.setFont("Serif-Bold", 11.5)
c.drawString(MARGIN, y, "Свободный")

y -= 6.5 * mm
y = draw_wrapped(
    MARGIN, y,
    "Чёрные джинсы вполне заменят брюки, а кроссовки — туфли.",
    CONTENT_W, size=9.8, leading=4.6 * mm,
)

y -= 8.5 * mm
y = draw_wrapped(
    MARGIN, y,
    "Если получится — будем рады спокойным пастельным оттенкам. Но главное — чтобы вам было красиво и удобно.",
    CONTENT_W, size=9.8, leading=4.6 * mm,
)

y -= 10 * mm
divider(y)

# ---------- parting quote (fills the space before the footer) ----------
mid_y = (y + FOOTER_H) / 2

c.setStrokeColorRGB(*GOLD)
c.setLineWidth(1)
c.circle(W / 2, mid_y + 13.5 * mm, 3.4 * mm, stroke=1, fill=0)
c.setFillColorRGB(*GOLD)
c.circle(W / 2, mid_y + 13.5 * mm, 0.7 * mm, stroke=0, fill=1)

c.setFillColorRGB(*STONE)
c.setFont("Serif-Italic", 12.5)
c.drawCentredString(W / 2, mid_y + 1.5 * mm, "Очень ждём этого дня")
c.drawCentredString(W / 2, mid_y - 4.7 * mm, "и встречи с вами!")

# ---------- footer / contacts ----------
c.setFillColorRGB(*PINE)
c.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)

c.setFillColorRGB(*GOLD_LIGHT)
c.setFont("Mono", 7.5)
c.drawString(MARGIN, 24 * mm, "ЕСЛИ ПОТЕРЯЕТЕСЬ")

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Bold", 14)
c.drawString(MARGIN, 17.5 * mm, "Кирилл")

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif", 11)
c.drawString(MARGIN, 11.5 * mm, "+7 910 966 64 02")

c.setFillColorRGB(*MIST)
c.setFont("Mono", 8.5)
c.drawString(MARGIN, 6 * mm, "@tepa46")

divider_x = W / 2 + 6 * mm
c.setStrokeColorRGB(*GOLD)
c.setLineWidth(0.4)
c.line(divider_x, 6 * mm, divider_x, FOOTER_H - 6 * mm)

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Italic", 10.5)
c.drawString(divider_x + 6 * mm, 17.5 * mm, "Спасибо,")
c.drawString(divider_x + 6 * mm, 12 * mm, "что будете")
c.drawString(divider_x + 6 * mm, 6.5 * mm, "рядом с нами.")

# ---------------------------------------------------------
c.showPage()
c.save()
print("done")
