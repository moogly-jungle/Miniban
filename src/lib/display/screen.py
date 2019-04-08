# coding: utf8
import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
# import util

class Screen:
    def __init__(self):
        self.epd = epd2in7.EPD()
        self.epd.init()
        self.epd.Clear(0xFF)
        self.lines = []

    def clear(self):
        self.lines = []
        
    def push_line(self, msg):
        self.lines.append(msg)
        
    def show(self):
        Limage2 = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Limage2)
        font12 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 12)

        Y0 = 80
        line_height = 10
        for k in range(self.lines):
            draw.text((0, Y0 + k*line_height), self.lines[k], font = font12, fill = 0)
        # draw.line((0, 90, epd2in7.EPD_WIDTH, 90), fill = 0)
        bmp = Image.open('explorer-logo.bmp')
        Limage2.paste(bmp, (0,0))
        self.epd.display(self.epd.getbuffer(Limage2))
        self.epd.sleep()
