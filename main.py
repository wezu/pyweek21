import __builtin__ as builtins
from panda3d.core import loadPrcFileData
loadPrcFileData("", "window-type none")
loadPrcFileData("", "sync-video 0")
loadPrcFileData("", "framebuffer-srgb true")
from direct.showbase.AppRunnerGlobal import appRunner
if appRunner: #run from binary/p3d
    path=appRunner.p3dFilename.getDirname()+'/'
else:  #run from python 
    path=''
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
             'shadow-area':400,
             'srgb':True,
             'hardware-skinning':True }
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
