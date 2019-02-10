# coding: utf8
import util
import term_util as term

def warning(str):
    term.pp('[warning] ', style=['red'])
    term.ppln(str)
