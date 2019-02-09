# coding: utf8

from time import *

class Chrono:
    def __init__(self):
        self.reset()

    def reset(self):
        self.t0 = time()
        self.t1 = self.t0
        
    def elapsed(self):
        # return the elapsed time from the last reset in sec
        return time() - self.t0

    def measure(self):
        # return the time from the last measure or reset
        t = time() - self.t1
        self.t1 = time()
        return t
        
