# coding: utf8
import log
import params
import time
import pypot.dynamixel
import term_util as term
import camera
import util
import importlib

servo_names = ["avant gauche", "arrière gauche",
              "avant droit", "arrière droit"]

class Robot:

    def __init__(self):
        term.pp("- connexion aux moteurs ... ")
        try:
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
            term.ppln("ok", style = ['green'])
            self.check()
            self.ready = True
        except:
            term.ppln("error", style = ['red'])
            self.ready = False
        self.camera = camera.Camera()

    def is_ready(self):
        return self.ready

    def check(self):
        temps = self.motor_temperature()
        voltages = self.motor_voltage()
        term.ppln('- check moteurs:')
        all_ok = True
        for m in range(4):
            t = temps[m]
            v = voltages[m]
            v_str = "%0.2f" % v
            term.pp('  ['+servo_names[m]+'] \ttemp: ' + str(t) + '° ')
            term.pp('\tvolt: ' + v_str + 'V ')
            if t < 50 and v > 9.98:
                term.ppln(' \t[ok]', style=['green'])
            else:
                term.ppln(' \t[error]', style=['red'])
                all_ok = False
        if not all_ok:
            log.warning('probleme moteur')
            
    
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
        nvg = util.bound(v_gauche, -params.max_power, params.max_power)
        nvd = util.bound(v_droite, -params.max_power, params.max_power)
        if not nvg == v_gauche or \
           not nvd == v_droite:
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

    def recule(self, v, duree=0):
        self.roule(-v,-v,duree)

    def pivote(self, v, duree=0):
        self.roule(v,-v,duree)

    def help(self):
        with open('src/robot/help.txt') as f:
            for line in f:
                print line,

    def play(self, module_name):
        try:
            m = importlib.import_module(module_name)        
            reload(m)
            m.play(self)
        except:
            term.ppln('erreur avec le module ' + module_name)
