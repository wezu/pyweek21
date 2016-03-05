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
from toolkit import loadObject
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
        self.grass.setMap(path+'levels/gandg2/grass.png')     
        self.grass_to_cut=self.grass.getStatus()
        # Car
        self.car=Car(self.world, self.worldNP)
        self.car.setPos(161.0,160.0,26)
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
        
        
        #map objects .. hardcoded because of time
        self.object_root=render.attachNewNode('object_root')
        obj=[
            (path+'models/pyweek_wall1',0.0,(303.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(301.0,405.0,25.0980434417725)),
            (path+'models/pyweek_wall1',0.0,(299.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(297.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(295.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(293.0,405.0,25.0980434417725)),
            (path+'models/pyweek_wall1',0.0,(291.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(289.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(287.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(285.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(283.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(281.0,405.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(281.0,385.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(283.0,385.0,25.0980453491211)),
            (path+'models/pyweek_wall1',0.0,(285.0,385.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,404.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,402.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,400.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,398.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,396.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,394.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(304.0,392.0,25.237850189209)),
            (path+'models/pyweek_wall1',90.0,(280.0,404.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,398.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,396.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,394.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,392.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,390.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,388.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,386.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(286.0,386.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(286.0,388.0,25.0980415344238)),
            (path+'models/pyweek_wall1',90.0,(286.0,390.0,25.0980434417725)),
            (path+'models/pyweek_wall1',0.0,(287.0,391.0,25.0980415344238)),
            (path+'models/pyweek_wall1',0.0,(289.0,391.0,25.1190624237061)),
            (path+'models/pyweek_wall1',0.0,(291.0,391.0,25.1960334777832)),
            (path+'models/pyweek_wall1',0.0,(293.0,391.0,25.1596641540527)),
            (path+'models/pyweek_wall1',0.0,(295.0,391.0,25.2697868347168)),
            (path+'models/pyweek_wall1',0.0,(297.0,391.0,25.3282146453857)),
            (path+'models/pyweek_wall1',0.0,(299.0,391.0,25.3496627807617)),
            (path+'models/pyweek_wall1',0.0,(301.0,391.0,25.2688617706299)),
            (path+'models/pyweek_wall1',0.0,(303.0,391.0,25.2534332275391)),
            (path+'models/pyweek_box',0.0,(279.600006103516,401.700012207031,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(279.399993896484,402.200012207031,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(279.600006103516,402.700012207031,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(279.399993896484,403.399993896484,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(278.799987792969,402.799987792969,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(278.799987792969,402.100006103516,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(279.0,401.5,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(278.5,401.600006103516,25.0980415344238)),
            (path+'models/pyweek_box',0.0,(278.799987792969,401.899993896484,25.5980415344238)),
            (path+'models/pyweek_wall1',90.0,(280.0,402.0,25.0980415344238)),
            (path+'models/pyweek_box',90.0,(279.5,402.600006103516,25.5980415344238)),
            (path+'models/pyweek_box',90.0,(279.0,402.5,25.5980415344238)),
            (path+'models/pyweek_box',90.0,(279.399993896484,402.0,25.5980415344238)),
            (path+'models/pyweek_box',90.0,(278.100006103516,402.299987792969,25.0980415344238)),
            (path+'models/pyweek_box',90.0,(277.799987792969,401.700012207031,25.0980415344238)),
            (path+'models/pyweek_box',90.0,(278.200012207031,401.899993896484,25.5980415344238)),
            (path+'models/pyweek_box',90.0,(279.399993896484,402.399993896484,26.0980415344238)),
            (path+'models/pyweek_box',90.0,(279.0,401.899993896484,26.0980415344238)),
            (path+'models/pyweek_box',90.0,(278.799987792969,402.399993896484,26.0980415344238))
            ]
        for i in obj:
            loadObject(model=i[0], H=i[1], pos=i[2], world=self.world, worldNP=self.worldNP, root=self.object_root, collision_solid=None)
        self.object_root.flattenStrong()
        
        #models/pyweek_gate,90.0,(280.0,399.0,25.0980415344238))
        
        #gui    
        self.hud=HUD()
        


