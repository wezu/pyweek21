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
from sky import Sky
from terrain import Terrain
from grass import Grass
from hud import HUD
from postprocess import Postprocess

DRIVING=1
WALKING=2
EXITING=3

class Game(DirectObject):
    def __init__(self):      
        #the window props should be set by this time, but make sure 
        wp = WindowProperties.getDefault()                  
        wp.setUndecorated(False)          
        wp.setFullscreen(False)     
        wp.setSize(800, 600)   
        #these probably won't be in the config (?)
        wp.setOrigin(-2,-2)  
        wp.setFixedSize(False)  
        wp.setTitle("PyWeek 21")
        #open the window
        base.openMainWindow(props = wp)  
          
        base.setBackgroundColor(0.1, 0.1, 0.8, 1)
        base.setFrameRateMeter(True)
        base.disableMouse()   
        
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
        self.accept('shift', self.shear)
        self.accept( 'window-event', self.onWindowEvent)
        
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'q')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'e')
        inputState.watchWithModifiers('turnLeft', 'a')
        inputState.watchWithModifiers('turnRight', 'd')

        # Task
        taskMgr.add(self.update, 'updateWorld') 
        taskMgr.doMethodLater(5.0, self.countGrass, 'grass_counter')
        
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
        
    def onWindowEvent(self,window=None):
        if window is not None: # window is none if panda3d is not started             
            self.filters.update()            
            self.hud.updateGuiNodes() 
            

    def countGrass(self, task):
        current=self.grass.getStatus()
        if self.grass_to_cut ==0:
            self.grass_to_cut=current
        v= (float(current)/float(self.grass_to_cut))
        #print self.grass_to_cut,  current
        self.hud.counter['text']= str(int(v*100.0))+"%"
        return task.again
        
    def update(self, task):
        dt = globalClock.getDt()
        
        if self.mode==DRIVING:
            self.car.drive(dt)
            self.hud.showSpeed(self.car.getKmph())
            self.hud.showFuel(self.car.fuel)
            self.grass.setMowerPos(self.car.blade_node)
            self.hud.grradar_display['frameTexture']=self.grass.gradar['tex']
            node_to_follow=self.car.node
            speed=0.3
        elif self.mode==WALKING:    
            self.char.walk(dt)
            node_to_follow=self.char.actor_node
            speed=0.03
        self.world.doPhysics(dt, 10, 0.001)
        if self.mode!=EXITING:
            self.camera.follow(node_to_follow, dt, speed)
        return task.cont

    def cleanup(self):
        self.world = None
        self.worldNP.removeNode()
    
    def _setMode(self, mode):
        self.mode=mode
        self.camera.zoomIn()
        
    def changeMode(self):
        if self.mode==DRIVING:
            if self.car.stopEngine():
                self.car.exitCar()
                self.char.exitCar(self.car.node)
                #self.char.getOutOfCar(self.car.node)
                Sequence(Wait(3.6), Func(self._setMode, WALKING)).start()
                self.mode=EXITING
                #self.camera.zoomIn()
                self.hud.hide()
        elif self.mode==WALKING:
            if abs(self.char.node.getDistance(self.car.node))<2.0:
                #if self.char
                self.mode=DRIVING
                self.camera.zoomOut()
                self.hud.show()
                self.char.enterCar()
                self.car.enterCar()
                #self.car.node.node().setMass(self.car.mass)
            
    def doFlip(self):
        if self.mode==DRIVING:
            self.car.flip()
            self.grass.getStatus()
        if self.mode==WALKING:
            self.char.jump()
    
    def shear(self):
        if self.mode==DRIVING:
            if self.car.blade_spining:
                self.car.blade_spining=False
                self.grass.mower_blade.hide()
            else:    
                self.car.blade_spining=True
                self.grass.mower_blade.show()
                
    def setup(self):
        self.worldNP = render.attachNewNode('World')

        # World
        self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.hide()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # Plane
        #shape = BulletPlaneShape(Vec3(0, 0, 1), 0)        
        #mesh = BulletTriangleMesh()
        #geomNodes = loader.loadModel('levels/test1/collision').findAllMatches('**/+GeomNode')
        #geomNode = geomNodes.getPath(0).node()
        #geom = geomNode.getGeom(0)
        #mesh.addGeom(geom)
        #shape = BulletTriangleMeshShape(mesh, dynamic=False, bvh=True )                
        #np = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
        #np.node().addShape(shape)
        #np.setPos(0, 0, -1.0)
        #np.setCollideMask(BitMask32.allOn())
        #self.world.attachRigidBody(np.node())

        #sky dome
        self.sun_sky=Sky()
        self.sun_sky.setTime(16.0)
        
        #terrain
        self.ground=Terrain(self.world, self.worldNP)        
        self.ground.loadMesh(path+'levels/gandg2/collision')
        self.ground.setMaps(path+'levels/gandg2/')        
        #TODO : this is stupid! |   |
        #                      \|/ \|/
        self.ground.setTexturesByID(39, 1)
        self.ground.setTexturesByID(1, 2)
        self.ground.setTexturesByID(2, 3)
        self.ground.setTexturesByID(15, 4)
        self.ground.setTexturesByID(4, 5)
        self.ground.setTexturesByID(5, 6)   
        #grass
        self.grass=Grass()
        self.grass.setMap(path+'levels/gandg/grass.png')     
        self.grass_to_cut=self.grass.getStatus()
        # Car
        self.car=Car(self.world, self.worldNP)
        self.car.setPos(256, 256, 40)
        #camera
        self.camera=FlyingCamera()
        
        #car to character scale 0.0128        
        self.char=Character(self.world, self.worldNP)        
        self.char.enterCar()
        #self.char.setPos(256, 250, 80)
        
        #filter manager, post process
        self.filters=Postprocess()        
        self.filters.setupFxaa() 
        #no time to make it work, sorry...
        #self.filters.setupFilters()
        
        
        self.hud=HUD()
        


