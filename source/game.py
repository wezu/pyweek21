import sys

from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.bullet import *

from car import Car
from flying_camera import FlyingCamera
from character import Character

DRIVING=1
WALKING=2

class Game(DirectObject):
    def __init__(self):      
        #the window props should be set by this time, but make sure 
        wp = WindowProperties.getDefault()                  
        wp.setUndecorated(False)          
        wp.setFullscreen(False)     
        wp.setSize(800,600)   
        #these probably won't be in the config (?)
        wp.setOrigin(-2,-2)  
        wp.setFixedSize(False)  
        wp.setTitle("PyWeek 21")
        #open the window
        base.openMainWindow(props = wp)  
          
        base.setBackgroundColor(0.1, 0.1, 0.8, 1)
        base.setFrameRateMeter(True)
        base.disableMouse()   
        
        # Light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alightNP = render.attachNewNode(alight)

        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(1, 1, -1))
        dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlightNP = render.attachNewNode(dlight)

        render.clearLight()
        render.setLight(alightNP)
        render.setLight(dlightNP)

        cm = CardMaker("plane")
        cm.setFrame(0, 512, 0, 512)
        self.grid=render.attachNewNode(cm.generate())
        self.grid.lookAt(0, 0, -1)
        self.grid.setTexture(loader.loadTexture('grid.png'))
        self.grid.setTransparency(TransparencyAttrib.MDual)
        self.grid.setTexScale(TextureStage.getDefault(), 32, 32, 1)
        self.grid.setZ(-1)
        self.grid.setLightOff()
        self.grid.setColor(0,0,0,0.5)

        self.mode=DRIVING
        
        # Input
        self.accept('escape', self.doExit)
        self.accept('r', self.doReset)
        self.accept('f1', self.toggleWireframe)
        self.accept('f2', self.toggleTexture)
        self.accept('f3', self.toggleDebug)
        self.accept('f5', self.doScreenshot)
        self.accept('space', self.doFlip)
        self.accept('tab', self.changeMode)

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('turnLeft', 'q')
        inputState.watchWithModifiers('turnRight', 'e')

        # Task
        taskMgr.add(self.update, 'updateWorld') 
        
        # Physics
        self.setup()
        
        # _____HANDLER_____

    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def doReset(self):
        self.cleanup()
        self.setup()

    def toggleWireframe(self):
        base.toggleWireframe()

    def toggleTexture(self):
        base.toggleTexture()

    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()

    def doScreenshot(self):
        base.screenshot('Bullet')

  # ____TASK___

    def update(self, task):
        dt = globalClock.getDt()
        
        if self.mode==DRIVING:
            self.car.drive(dt)
            node_to_follow=self.car.node
        elif self.mode==WALKING:    
            self.char.walk(dt)
            node_to_follow=self.char.node
            
        self.world.doPhysics(dt, 10, 0.001)
        self.camera.follow(node_to_follow, dt)
        return task.cont

    def cleanup(self):
        self.world = None
        self.worldNP.removeNode()
    
    def changeMode(self):
        if self.mode==DRIVING:
            if self.car.stopEngine():
                self.mode=WALKING
                if self.char.node.node() not in self.world.getCharacters():
                    self.world.attach(self.char.node.node())
        elif self.mode==WALKING:
            self.mode=DRIVING
            
    def doFlip(self):
        if self.mode==DRIVING:
            self.car.flip()
        
        if self.mode==WALKING:
            self.char.jump()
            
    
    def setup(self):
        self.worldNP = render.attachNewNode('World')

        # World
        self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # Plane
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)

        np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
        np.node().addShape(shape)
        np.setPos(0, 0, -1)
        np.setCollideMask(BitMask32.allOn())

        self.world.attachRigidBody(np.node())

        # Car
        self.car=Car(self.world, self.worldNP)
        #self.world.remove(self.car.vehicle)
        #self.car.startEngine()    
        #camera
        self.camera=FlyingCamera(offset=(0, -5, 1.8), angle=-10)
        
        #car to character scale 0.0128
        
        self.char=Character(self.world, self.worldNP)
        
        self.char.setPos(10, 10, 0)

        


