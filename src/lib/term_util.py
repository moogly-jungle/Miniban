#
# y = 6, x = 3 print("\033[6;3HHello")
# backspace = \b
# line up: "\033[F"
# beep: print("\a")
# clear line from the cursor: "\033[1K"
# clear all the line "\033[2K"

# test: print("\033[6;3H"\033[2K"Hello")
# clear screen print("\033[2J")

# https://en.wikipedia.org/wiki/ANSI_escape_code

# reset color: print("\033[0m")
# bold: print("\033[1m")
# underline: print("\033[4m")
# blink: print("\033[5m")
# inverse: print("\033[7m")
# print("\033[30m") print("\033[31m") ... print("\033[37m") text color:
# Black 	Red 	Green 	Yellow[16] 	Blue 	Magenta 	Cyan 	White
# print("\033[40m") print("\033[41m") ... print("\033[47m") background color:
# print("\033[38;2;100;0;0mHello\033[0m")

import sys
import util
import time
import getch
import calendar
import datetime
import params

###############################################################################

def output(str):
    sys.stdout.write(str)
    sys.stdout.flush()

def clear():
    output("\033[2J")

def goto(x,y):
    output("\033["+str(y)+";"+str(x)+"H")

def goto_column(x):
    output("\033[" + str(x) + "G")
    
def beep():
    if not params.term_silent: output("\a")

def bold():
    output("\033[1m")
    
def underline():
    output("\033[4m")
    
def reset_color():
    output("\033[0m")
    
def inverse_color():
    output("\033[7m")

def line_begin():
    output("\033[1G")

def line_up():
    output("\033[F")

def clear_line():
    output("\033[2K")

# TODO: ne marche pas ...
def clear_line_from_cursor():
    output("\033[1K")
        
def backspace():
    output("\b")
    
def blink():
    output("\033[5m")

def save_cursor_pos():
    output("\033[s")

def restore_cursor_pos():
    output("\033[u")
             
class TermColor:
    VIOLET = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def endl():
    output('\n')

def pp(str, style = []):
    for s in style:
        if s == 'blink': blink()
        if s == 'inverse': inverse_color()
        if s == 'bold': bold()
        if s == 'underline': underline()
        if s == 'violet': output(TermColor.VIOLET)
        if s == 'blue': output(TermColor.BLUE)
        if s == 'green': output(TermColor.GREEN)
        if s == 'yellow': output(TermColor.YELLOW)
        if s == 'red': output(TermColor.RED)
    output(str)
    reset_color()
    sys.stdout.flush()

def ppln(str, style = []):
    pp(str,style)
    endl()
    
def nice_print(str, option = []):    
    for n in range(len(str)):
        pp(str[n], option)
        if not params.term_immediate and util.contains(option,'beep'): beep()
        if not params.term_immediate and not util.contains(option, 'immediate'): time.sleep(0.05)
    if not params.term_immediate and util.contains(option,'pause'): time.sleep(0.5)
    reset_color()

def user_pause():
    nice_print("- press a key to continue ... ", option = ['blink', 'immediate'])
    c = getch.getch()
    clear_line()
    line_begin()
    
def filter_formatting_mark(text):
    bad_char = [ TermColor.VIOLET, TermColor.BLUE, TermColor.GREEN, TermColor.YELLOW, TermColor.RED, TermColor.ENDC, TermColor.BOLD, TermColor.UNDERLINE ]
    for c in bad_char:
        text = text.replace(c,'')
    return text

def html_format(text):
    text = text.replace('\n','<br>')
    text = text.replace('\t','&nbsp&nbsp')
    text = text.replace(' ','&nbsp')
    state = []
    new_text = ''
    i=0
    while i < len(text):
        if text[i:i+len(TermColor.ENDC)] == TermColor.ENDC:
            if state != []:
                tag = state.pop()
                new_text += tag
                i += len(TermColor.ENDC)
                continue
        found = False
        for mark in [ [TermColor.BOLD, '<b>', '</b>'],
                      [TermColor.UNDERLINE, '<u>', '</u>'],
                      [TermColor.GREEN, '<b><font color="green">', '</font></b>'],
                      [TermColor.VIOLET, '<b><font color="purple">', '</font></b>'],
                      [TermColor.BLUE, '<b><font color="blue">', '</font></b>'],
                      [TermColor.YELLOW, '<b><font color="yellow">', '</font></b>'],
                      [TermColor.RED, '<b><font color="red">', '</font></b>'] ]:
            if text[i:i+len(mark[0])] == mark[0]:
                new_text += mark[1]
                i += len(mark[0])
                state.append(mark[2])
                found = True
                break
        if not found:
            new_text += text[i]
            i += 1
            
    text = new_text
    text = filter_formatting_mark(text)
    return text

def separator():
    print("-----------------------------------------------------------------------------")

def print_ok():
    bold()
    output(TermColor.GREEN + 'ok' + TermColor.ENDC)
    endl()
    
def print_ko():
    bold()
    blink()
    output(TermColor.RED + 'ko' + TermColor.ENDC)
    beep()
    endl()

def warning(str):
    output(TermColor.YELLOW)
    output("warning : " + str)
    output(TermColor.ENDC)
    endl()

def print_time(unix_t):
    return time.strftime("%Y/%m/%d-%H:%M:%S UTC", time.gmtime(unix_t))

def print_array(width, M, unit = [], legend = None, widths = []):
    L = len(M) 
    if L == 0: return
    C = len(M[0])
    if C == 0: return
    if legend is not None:
        for i in range(len(legend)):
            goto_column(i * width)
            pp(legend[i], style = ['bold'])
            if not unit == []: pp(" " + unit[i])
        endl()

    p=0
    for l in M:
        if p%2==0: sty = ['bold']
        else: sty = []
        for i in range(len(l)):
            if widths == []:
                goto_column(i * width)
            else:
                goto_column(widths[i])
            if isinstance(l[i], float):
                pp("%0.3f" % (l[i]), style = sty)
            else:
                pp(l[i], style = sty)
            if not unit == []: pp(" " + unit[i], style = sty)
        endl()
        p += 1

