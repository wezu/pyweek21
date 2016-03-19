import __builtin__ as builtins
from panda3d.core import loadPrcFileData
from direct.showbase.AppRunnerGlobal import appRunner
if appRunner: #run from binary/p3d
    path=appRunner.p3dFilename.getDirname()+'/'
else:  #run from python 
    path=''
try:    
    f = open(path+'config.txt', 'r')
    for line in f:        
        if not line.startswith('#'):        
            loadPrcFileData('',line)          
except IOError:
    if not appRunner:    
        print "No config file, using default"   
loadPrcFileData("", "window-type none")
loadPrcFileData("", "textures-power-2 None")        
loadPrcFileData("", "framebuffer-srgb True")        
from panda3d.core import *
from direct.showbase import ShowBase
import sys


DEBUG=3
INFO=2
WARNING=1
ERROR=0

class App():
    def __init__(self):
        #init ShowBase
        base = ShowBase.ShowBase()        
        #make the path a builtin
        builtins.path=path
        
        cfg={'simple-shaders':False,
             'shadow-size':1024,
             'shadow-area':50,
             'srgb':True,
             'hardware-skinning':True }
             
        cfg['hardware-skinning']=ConfigVariableBool('hardware-skinning', True).getValue()     
        cfg['srgb']=ConfigVariableBool('framebuffer-srgb', False).getValue()
        cfg['win-size']=[ConfigVariableInt('win-size', '640 480').getWord(0), ConfigVariableInt('win-size', '640 480').getWord(1)] 
        cfg['music-volume']=ConfigVariableInt('music-volume', '50').getValue()
        cfg['sound-volume']=ConfigVariableInt('sound-volume', '100').getValue()
        cfg['key-forward']=ConfigVariableString('key-forward','w').getValue()
        cfg['key-back']=ConfigVariableString('key-back','s').getValue()
        cfg['key-left']=ConfigVariableString('key-left','a').getValue()
        cfg['key-right']=ConfigVariableString('key-right','d').getValue()
        cfg['key-jump']=ConfigVariableString('key-jump','space').getValue()
        cfg['key-cut-grass']=ConfigVariableString('key-cut-grass','shift').getValue()
        cfg['key-enter-exit-car']=ConfigVariableString('key-enter-exit-car','tab').getValue()
        cfg['shadow-size']=ConfigVariableInt('shadow-size',1024).getValue()
        cfg['shadow-area']=ConfigVariableInt('shadow-area',50).getValue()
             
        builtins.cfg=cfg
        
        self.info_level=DEBUG
        
        self.startGame()
        
    def startGame(self):
        self.info("Starting game",DEBUG)
        sys.path.append(path+"source")
        from game import Game
        self.game=Game()    
        self.info("Game Started",INFO)
        
    def exit(self):
        self.info("APP EXIT!",DEBUG)
        base.userExit()
        
    def info(self, txt, level=INFO):      
        if level <= self.info_level:
            if level==INFO:
                txt= "(Info): "+txt
            elif level==DEBUG:
                txt= "(Debug): "+txt
            elif level==WARNING:
                txt= "(WARNING): "+txt
            elif level==ERROR:
                txt= "(ERROR!): "+txt            
            print txt
            
g=App()
base.run()
