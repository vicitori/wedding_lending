# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

# ---------------------------------------------------------
# Fonts
# ---------------------------------------------------------
pdfmetrics.registerFont(TTFont("Serif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Mono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"))

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

# ---------------------------------------------------------
# Ссылки для QR — замени на свои!
# ---------------------------------------------------------
QR_UPLOAD_URL = "https://example.com/upload"      # куда гости загружают свои фото
QR_GALLERY_URL = "https://example.com/gallery"    # папка с фото от фотографа

c = canvas.Canvas("/home/claude/checklist.pdf", pagesize=A5)

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


def draw_qr(x, y, size, data):
    """Рисует QR-код с левого-нижнего угла (x, y), сторона size."""
    qr = QrCodeWidget(data)
    b = qr.getBounds()
    w = b[2] - b[0]
    h = b[3] - b[1]
    d = Drawing(size, size, transform=[size / w, 0, 0, size / h, 0, 0])
    d.add(qr)
    renderPDF.draw(d, c, x, y)


# ===========================================================
# PAGE 1
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
    "Приехать к 8:30 на Стачек, 88",
    "Зарядить телефон",
    "Не брать цветы из города",
]
for item in todo:
    text_x = checkbox(MARGIN, y, text_size=9.8)
    c.setFillColorRGB(*INK)
    c.setFont("Serif", 9.8)
    c.drawString(text_x, y, item)
    y -= 7.5 * mm

y += 1.5 * mm
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
    ("08:30", "Автобус от Автово",
     "Yutong ждёт у метро Автово, ориентир — Стачек, 88. Госномер сообщим накануне. Ждём не дольше 5–10 минут."),
    ("≈ 10:30", "Парк Монрепо",
     "По дороге будет остановка размяться, в автобусе есть вода. На входе скажите, что вы по групповому билету на свадьбу."),
    ("11:00", "Церемония во дворце",
     "Регистрация проходит в дворце Монрепо. После официальной части — прогулка и фотографии в парке."),
    ("15:30", "Ресторан",
     "«Птички и ягоды», Приморское шоссе, 572. Едем туда тем же автобусом."),
    ("≈ 23:00", "Домой",
     "Тем же автобусом возвращаемся к метро Автово."),
]
for i, (time_label, title, text) in enumerate(route):
    is_last = i == len(route) - 1
    y = timeline_item(y, time_label, title, text, is_last=is_last)


# ===========================================================
# PAGE 2
# ===========================================================
new_page()
y = H - 16 * mm
FOOTER_H = 34 * mm

# ---------- important cards (2x2) ----------
section("Важно помнить", y)
y -= 9 * mm

left = MARGIN
right = W / 2 + 2 * mm
card_w = W / 2 - MARGIN - 4 * mm - BOX_TEXT_GAP

cards = [
    ("Позавтракайте", "Первый полноценный приём пищи будет только около 15:30.", left),
    ("Вода будет", "В автобусе есть питьевая вода, по дороге будет остановка.", right),
    ("Цветы не нужны", "Долгую дорогу не переживут — подарите при следующей встрече.", left),
    ("Фотограф", "Красивые кадры делаем во время прогулки в Монрепо.", right),
]

row1_y = y
row2_y = y - 22 * mm
for i, (title, text, x) in enumerate(cards):
    row_y = row1_y if i < 2 else row2_y
    text_x = checkbox(x, row_y, text_size=10)
    c.setFillColorRGB(*INK)
    c.setFont("Serif-Bold", 10)
    c.drawString(text_x, row_y, title)
    draw_wrapped(text_x, row_y - 4.6 * mm, text, card_w, size=8.4, leading=3.7 * mm)

y = row2_y - 16 * mm
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
    "Чёрные джинсы вполне заменят брюки, а кроссовки — туфли. Дамам будем рады видеть в спокойных пастельных оттенках, но главное — чтобы вам было красиво и удобно.",
    CONTENT_W, size=9.6, leading=4.5 * mm,
)
y -= 9 * mm
divider(y)
y -= 10 * mm

# ---------- QR block ----------
section("Фотографии", y)
y -= 8 * mm

# Два QR по бокам
QR_SIZE = 26 * mm
qr_gap = 8 * mm
total_qr_w = QR_SIZE * 2 + qr_gap
qr_left_x = (W - total_qr_w) / 2
qr_right_x = qr_left_x + QR_SIZE + qr_gap

qr_y_top = y  # верх зоны QR
qr_y = qr_y_top - QR_SIZE

# Рамки для акцента
c.setStrokeColorRGB(*GOLD)
c.setLineWidth(0.5)
c.rect(qr_left_x - 2 * mm, qr_y - 2 * mm, QR_SIZE + 4 * mm, QR_SIZE + 4 * mm, stroke=1, fill=0)
c.rect(qr_right_x - 2 * mm, qr_y - 2 * mm, QR_SIZE + 4 * mm, QR_SIZE + 4 * mm, stroke=1, fill=0)

draw_qr(qr_left_x, qr_y, QR_SIZE, QR_UPLOAD_URL)
draw_qr(qr_right_x, qr_y, QR_SIZE, QR_GALLERY_URL)

# Подписи под QR
label_y = qr_y - 6 * mm
c.setFillColorRGB(*PINE)
c.setFont("Serif-Bold", 9.5)
c.drawCentredString(qr_left_x + QR_SIZE / 2, label_y, "Ваши фото")
c.drawCentredString(qr_right_x + QR_SIZE / 2, label_y, "Фото от фотографа")

c.setFillColorRGB(*STONE)
c.setFont("Serif-Italic", 8.4)
c.drawCentredString(qr_left_x + QR_SIZE / 2, label_y - 5 * mm, "загрузить сюда")
c.drawCentredString(qr_right_x + QR_SIZE / 2, label_y - 5 * mm, "появятся позже")

# Общий подзаголовок над QR
c.setFillColorRGB(*INK)
c.setFont("Serif", 9.3)
c.drawCentredString(
    W / 2, qr_y_top + 2 * mm,
    "Скиньте свои кадры сюда — и здесь же появится папка от фотографа."
)

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
c.drawString(MARGIN, 11.5 * mm, "+7 910 966 6402")

c.setFillColorRGB(*MIST)
c.setFont("Mono", 8.5)
c.drawString(MARGIN, 6 * mm, "@tepa46")

divider_x = W / 2 + 6 * mm
c.setStrokeColorRGB(*GOLD)
c.setLineWidth(0.4)
c.line(divider_x, 6 * mm, divider_x, FOOTER_H - 6 * mm)

c.setFillColorRGB(*PARCHMENT)
c.setFont("Serif-Italic", 10.5)
c.drawString(divider_x + 6 * mm, 20 * mm, "Очень ждём")
c.drawString(divider_x + 6 * mm, 14.5 * mm, "этого дня")
c.drawString(divider_x + 6 * mm, 9 * mm, "и встречи")
c.drawString(divider_x + 6 * mm, 3.5 * mm, "с вами!")

# ---------------------------------------------------------
c.showPage()
c.save()
print("done")