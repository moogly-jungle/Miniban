# coding: utf8
import params
import sys

sys.path.append(params.base_dir + '/src')
sys.path.append(params.base_dir + '/src/lib')
sys.path.append(params.base_dir + '/src/robot')
sys.path.append(params.base_dir + '/src/exemples')

import term_util as term

term.separator()
term.ppln('Bienvenue dans le terminal de commande du robot')
term.ppln('- A tout moment tu peux taper "bot.help()" pour avoir un peu d\'aide')
term.separator()

term.ppln('[initialisation du robot]', style=['green'])
import robot
bot = robot.Robot()

term.endl()
if bot.is_ready():
    term.ppln('[robot operationnel, tape une commande]', style=['green'])
else:
    term.ppln('[problème dans l\'initialisation du robot]', style=['red'])
term.endl()

sys.ps1 = 'miniban> '

