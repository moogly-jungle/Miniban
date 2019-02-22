# coding: utf8
import numpy as np
import log
import params
import time
import pypot.dynamixel
import term_util as term
import camera
import util
import importlib
import imu_reader
from pypot.dynamixel.protocol.v1 import DxlReadDataPacket

servo_names = ["avant gauche", "arrière gauche",
              "avant droit", "arrière droit"]

class Robot:

    def __init__(self):
        self.ready = True
        try:
            term.pp("- connexion aux moteurs ... ")
            ports = pypot.dynamixel.get_available_ports()
            self.dxl = pypot.dynamixel.DxlIO(ports[0], baudrate=1000000)
            self.left_up = 1
            self.left_down = 6
            self.right_up = 7
            self.right_down = 15
            self.servos = [self.left_up, self.left_down, \
                           self.right_up, self.right_down]
            self.dxl.set_wheel_mode(self.servos)
            time.sleep(0.5)
            self.temperatures = self.motor_temperature()
            term.ppln("[ok]", style = ['green'])
        except:
            term.ppln("error", style = ['red'])
            self.ready = False

        term.pp("- connexion à la caméra ... ")
        self.camera = camera.Camera()
        if self.camera.ready: term.ppln('[ok]', style = ['green'])
        else: term.ppln("error", style = ['red'])

        term.pp("- calibration de l'imu ... ")
        self.imu = imu_reader.ImuReader(self)
        self.imu.start()
        time.sleep(0.250)
        self.imu.calib(3)
        time.sleep(3)
        self.imu.reset_orientation()
        term.ppln('[ok]', style = ['green'])
        
        self.check()
            
    def is_ready(self):
        return self.ready

    def check(self):
        all_ok = True
        term.ppln('- initialisation procédure de test globale')
        term.ppln('  - check moteurs:')
        try:
            temps = self.motor_temperature()
            voltages = self.motor_voltage()
            for m in range(4):
                t = temps[m]
                v = voltages[m]
                v_str = "%0.2f" % v
                term.pp('    ['+servo_names[m]+'] \ttemp: ' + str(t) + '° ')
                term.pp('\tvolt: ' + v_str + 'V ')
                if t < 50 and v > 9.98:
                    term.ppln(' \t[ok]', style=['green'])
                else:
                    term.ppln(' \t[error]', style=['red'])
                    all_ok = False
        except:
            term.ppln('    [erreur]', style=['red'])
        term.ppln('  - check capteurs:')
        dist_sensors = ['avant', 'droite', 'gauche']
        for s in dist_sensors:
            term.pp('    [dist. ' + s + '] ... ') 
            if self.check_distance_sensor(s):
                term.ppln('[ok]', style=['green'])
            else:
                term.ppln('[erreur]', style=['red'])
                all_ok = False

        term.pp('    [camera] ... ')
        if self.camera.ready:
            term.ppln('[ok]', style=['green'])
        else:
            term.ppln('[erreur]', style=['red'])
            all_ok = False

        if all_ok:
            term.pp('- procédure de test globale ... ')
            term.ppln('[ok]', style=['green'])
        else:
            log.warning('Erreur procédure de test')

                
    def motor_temperature(self):
        """ return the temperature of all the motors (deg) """
        return self.dxl.get_present_temperature(self.servos)

    def motor_voltage(self):
        """ return the voltage of all the motors (V) """
        return self.dxl.get_present_voltage(self.servos)

    def photo(self, filename = 'image'):
        term.ppln('- Enregistrement de l\'image dans ' + filename +
                  '.' + self.camera.file_format())
        self.camera.take_photo(filename)
        
    def roule(self, v_gauche, v_droite, duree = 0):
        ratio = 0.026
        p_gauche = int(v_gauche / ratio)
        p_droite = int(v_droite / ratio)
        nvg = util.bound(p_gauche, -params.max_power, params.max_power)
        nvd = util.bound(p_droite, -params.max_power, params.max_power)
        if not nvg == p_gauche or \
           not nvd == p_droite:
            log.warning('vitesse trop grande, limitée à ' + str(params.max_power))
        self.dxl.set_moving_speed({self.left_up:nvg,
                                   self.left_down:nvg,
                                   self.right_up:-nvd,
                                   self.right_down:-nvd})
        if duree > 0:
            time.sleep(duree)
            self.dxl.set_moving_speed({1:0, 6:0, 7:0, 15:0})

    def avance(self, v, duree=0):
        self.roule(v,v,duree)

    def stop(self):
        self.roule(0,0)

    def recule(self, v, duree=0):
        self.roule(-v,-v,duree)

    def pivote(self, v, duree=0):
        self.roule(v,-v,duree)

    def help(self):
        with open('src/robot/help.txt') as f:
            for line in f:
                print (line, end='')

    def play(self, module_name):
        try:
            m = importlib.import_module(module_name)        
            reload(m)
            m.play(self)
        except:
            term.ppln('erreur avec le module ' + module_name)
        
    def adc_brut_values(self):
        N = 5
        sp = self.dxl._send_packet(DxlReadDataPacket(240, 36, N*2))
        values = []
        for i in range(N):
            v = sp.parameters[2*i] + 255*sp.parameters[2*i+1]
            values.append(v)
        return values

    def check_distance_sensor(self, pos, verbose=False):
        if pos is None :
            log.warning('check_distance_sensor: mauvaise valeur pour pos')
            return False
        N = 10
        echantillon = []
        for i in range(N):
            echantillon.append(self.distance(pos))
            time.sleep(0.05)
        echantillon = np.array(echantillon)
        stddev = np.std(echantillon)
        if verbose:
            term.ppln('check_distance_sensor. Echantillon de mesure:')
            term.ppln(str(echantillon))
            term.ppln('std dev: ' + str(stddev))
        return stddev > 0

    def distance(self, pos = None):
        """ donne la valeur des capteurs de distances (m)
            pos peut être None, 'avant', 'droite' ou 'gauche' """
        adc_values = self.adc_brut_values()
        pos_to_adc = { 'avant': 0, 'droite': 2, 'gauche': 3 } 
        adc_to_dist_sensor = [0,2,3] # the list of dist sensor from adc values
        a = -2.8571428571428563 # empirical values from measures
        b = 7421.938775510203   # on assume the transformation function
        c = 110.4285714285714   # to be of form a + b / (x+c)
        values = {}
        for p,idx in pos_to_adc.items():
            d = a + b / (adc_values[idx] + c)
            values[p] = d
        if pos is None: return values
        elif pos in [ 'avant', 'droite', 'gauche' ]:
            return values[pos]
        else:
            log.warning('capteur de distance inconnu (' + str(pos) + ')')
            return None
 
