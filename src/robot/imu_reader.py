# coding: utf8
import threading
import time
import pypot.dynamixel
from pypot.dynamixel.protocol.v1 import DxlReadDataPacket
import util
import copy
import chrono
import numpy as np

class ImuReader(threading.Thread):
    
    def __init__(self, robot):
        threading.Thread.__init__(self)
        self.mutex = threading.Lock()
        self.robot = robot

        self.accelero = np.array([0,0,0], dtype = np.float32)  # acceleration in g
        self.gyro = np.array([0,0,0], dtype = np.float32) # gyro in deg/sec
        self.gyro_zero = None
        self.magneto = np.array([0,0,0], dtype = np.float32) 
        self.orientation = 0.0
        self.imu_cycle = None

        self.count = 0
        self.frequency = None # frequency in Hz
        self.chrono = chrono.Chrono()
        self.tick_chrono = None
        self.dt = None
        self.ok = True

        self.calibration = False
        self.calib_chrono = None
        self.calib_idx = 0
        self.calib_duration = None
        
    def run(self):
        myok = self.ok
        while myok:
            if self.tick_chrono is None:
                self.tick_chrono = chrono.Chrono()
                self.dt = None
            else:
                self.dt = self.tick_chrono.measure()
            self.mutex.acquire()
            self.update_imu()
            self.calib_tick()
            if self.dt is not None: self.update_orientation()
            self.mutex.release()
            time.sleep(0.001)
            self.mutex.acquire()
            myok = self.ok
            self.count += 1
            if self.count % 100 == 0:
                delta_t = self.chrono.measure()
                period = delta_t / 100
                self.frequency = 1.0 / period
            self.mutex.release()

    def update_orientation(self):
        v = self.gyro[2] - self.gyro_zero[2] if self.gyro_zero is not None else self.gyro[2]
        self.orientation += self.dt * v

    def get_orientation(self):
        self.mutex.acquire()
        res = self.orientation
        self.mutex.release()
        return res

    def reset_orientation(self):
        self.mutex.acquire()
        self.orientation = 0.0
        self.mutex.release()
    
    def calib(self, duration = 3):
        if self.calibration: return
        self.mutex.acquire()
        self.calibration = True
        self.calib_idx = 0
        self.calib_chrono = chrono.Chrono()
        self.calib_duration = duration
        self.gyro_zero = np.array([0.0,0.0,0.0], dtype = np.float32)
        self.mutex.release()

    def calib_tick(self):
        if not self.calibration: return
        if self.calib_chrono.elapsed() > self.calib_duration:
            self.calibration = False
            self.calib_chrono.reset()
            return
        # one maintains the zero usable because we make it consistent
        # even during the calibration process.
        if self.calib_idx == 0:
            self.gyro_zero = np.array(self.gyro, dtype = np.float32)
        else:
            self.gyro_zero = (self.calib_idx * self.gyro_zero + self.gyro) / (self.calib_idx+1)
        self.calib_idx += 1

    # tells whether the gyro has been calibrated or not and
    # if yes: from how much time ? (in second)
    def calib_state(self):
        if self.gyro_zero is None: return None
        return self.calib_chrono.elapsed()
            
    # acceletation in 3 dimensions in g
    def get_acc(self):
        self.mutex.acquire()
        res = copy.deepcopy(self.accelero)
        self.mutex.release()
        return res

    # gyrometer in 3 dimensions in deg/sec
    def get_gyro(self):
        self.mutex.acquire()
        res = copy.deepcopy(self.gyro - self.gyro_zero if self.gyro_zero is not None else self.gyro)
        self.mutex.release()
        return res

    # magneto
    def get_magneto(self):
        self.mutex.acquire()
        res = copy.deepcopy(self.magneto)
        self.mutex.release()
        return res

    def update_imu(self):
        rp = DxlReadDataPacket(241, 36, 110)
        sp = self.robot.dxl._send_packet(rp)
        A = sp.parameters
        for l in range(5):
            ratio = 256.0
            for i in range(0,3):
                b1 = A[22*l+2*i]
                b2 = A[22*l+2*i+1]
                v = util.ubyte2short(b1,b2) / ratio
                self.accelero[i] = v
            ratio = 14.375
            for i in range(3,6):
                b1 = A[22*l+2*i]
                b2 = A[22*l+2*i+1]
                v = util.ubyte2short(b1,b2) / ratio
                self.gyro[i-3] = v
            for i in range(6,9):
                b1 = A[22*l+2*i]
                b2 = A[22*l+2*i+1]
                v = util.ubyte2short(b1,b2)
                self.magneto[i-6] = v
            b1 = A[22*l+18]
            b2 = A[22*l+19]
            b3 = A[22*l+20]
            b4 = A[22*l+21]
            v = util.ubyte2uint(b1,b2,b3,b4)
            self.imu_cycle = v
    
    def kill(self):
        self.mutex.acquire()
        self.ok = False
        self.mutex.release()

