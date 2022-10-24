import io

from PIL import Image, ImageDraw, ImageFont
import numpy

_desk = "apolo/static/base.png"
_bart = "apolo/static/bart.png"
_font_path = "apolo/static/comicsansms3.ttf"

OUT_FILE_PATH = "./out.jpg"

FONT_SIZE = 16
LINE_HEIGHT = FONT_SIZE * .9


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)


def render_mem(mess: str) -> io.BufferedReader:
    """
    Рендерит картинку с Бартом Симпсоном пишещим на доаске текст из `mess`
    """
    mess = mess[:54] if len(mess) >= 54 else mess

    with Image.open(_desk).convert("RGBA") as base:
        base.load()
        # Создаём пустую картинку
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
        # берем шрифт
        fnt = ImageFont.truetype(_font_path, FONT_SIZE)
        # создаём контекст
        d = ImageDraw.Draw(txt)

        # рисуем текст
        mess = mess.upper()
        for y in range(10):
            d.text((1, y * LINE_HEIGHT * 1.9), mess, font=fnt, fill=(255, 255, 255, 234))

        width, height = txt.size

        # Получаем коэф-ты для перспективы
        coeffs = find_coeffs(
            [(0, -70), (256, -90), (256, 250), (0, 256)],
            [(0, 0), (256, -60), (256, 256), (0, 250)]
        )

        txt = txt.transform((width, height), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

        tmp = Image.alpha_composite(base, txt)
        with Image.open(_bart).convert("RGBA") as bart_:
            out = Image.alpha_composite(tmp, bart_)
            out.save(OUT_FILE_PATH, "PNG")

        return OUT_FILE_PATH
