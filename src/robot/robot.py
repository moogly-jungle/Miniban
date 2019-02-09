# coding: utf8
import params
import time
import pypot.dynamixel
import term_util as term
import camera
import util

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
            term.pp("- température moteurs (deg): ")
            map(lambda x: term.pp(str(x) + " "), self.temperatures)
            term.endl()
            self.ready = True
        except:
            term.ppln("error", style = ['red'])
            self.ready = False
        self.camera = camera.Camera()

    def is_ready(self):
        return self.ready
        
    def motor_temperature(self):
        """ return the temperature of all the motors (deg) """
        return self.dxl.get_present_temperature(self.servos)
    
    def photo(self, filename = 'image'):
        term.ppln('- Enregistrement de l\'image dans ' + filename +
                  '.' + self.camera.file_format())
        self.camera.take_photo(filename)
        
    def roule(self, v_gauche, v_droite, duree = 0):
        v_gauche = util.bound(v_gauche, -params.max_power, params.max_power)
        v_droite = util.bound(v_droite, -params.max_power, params.max_power)
        self.dxl.set_moving_speed({self.left_up:v_gauche,
                                   self.left_down:v_gauche,
                                   self.right_up:-v_droite,
                                   self.right_down:-v_droite})
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
