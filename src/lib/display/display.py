# coding: utf8
import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import util
import term_util as term

class Display:
    def __init__(self):
        self.ready = False
        try:
            self.epd = epd2in7.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            self.lines = []
            self.show()
            self.ready = True
        except:
            pass
        
    def clear(self):
        self.lines = []
        
    def push_line(self, msg):
        self.lines.append(msg)

    def print_lines(self, msg_list):
        for l in msg_list: self.push_line(l)
        self.show()
        
    def show(self):
        img = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(img)
        font12 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 12)

        Y0 = 60
        line_height = 12
        margin = 5
        for k in range(len(self.lines)):
            draw.text((margin, Y0 + k*line_height), self.lines[k], font = font12, fill = 0)

        bigY = epd2in7.EPD_HEIGHT-46
        draw.line((0, bigY, epd2in7.EPD_WIDTH, bigY), fill = 0)
        draw.text((10, bigY+5), util.date(), font = font12, fill = 0)
        draw.text((10, bigY+17), 'connecté au réseau ' + util.get_essid(), font = font12, fill = 0)
        draw.text((10, bigY+29), 'adresse IP : ' + util.get_ip_address(), font = font12, fill = 0)
        bmp = Image.open('/home/pi/Miniban/src/lib/display/explorer-logo.bmp')
        img.paste(bmp, (0,0))
        self.epd.display(self.epd.getbuffer(img))
        self.clear()

    def kill(self):
        self.epd.sleep()
        term.ppln('- display system killed')
