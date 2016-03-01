from panda3d.core import *
from direct.showbase.InputStateGlobal import inputState
from panda3d.bullet import *

class Character():
    def __init__(self, world, worldNP):
         
        height = 0.7
        radius = 0.1
        shape = BulletCapsuleShape(radius, height - 2*radius, ZUp)
 
        self.controler = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.controler.setMaxJumpHeight(50.0)
        self.controler.setJumpSpeed(5.0)
        self.controler.setUseGhostSweepTest(True)
        #self.controler.setFallSpeed(0.5)
        playerNP = worldNP.attachNewNode(self.controler)
        playerNP.setCollideMask(BitMask32.allOn()) 
        world.attach(playerNP.node()) 
    
        self.model=loader.loadModel("models/rocket")
        self.model.reparentTo(playerNP)
        self.model.setH(180)
        self.model.setZ(-height/2.0)
        self.model.setScale(0.0128)
    
        self.node=playerNP
        self.world=world
        
    def hide(self):
        self.model.hide()
        self.world.remove(self.node.node())
    
    def show(self):
        self.model.hide()
        self.world.attach(self.node.node())
         
        
    def setPos(self, *args):
        pos=[]
        for arg in args:
            pos.append(arg)
        if len(pos)==1:                
            self.node.setPos(render, pos)
        elif len(pos)>2:        
            self.node.setPos(render, Vec3(pos[0],pos[1],pos[2]))
            
    def jump(self):
        self.controler.doJump()  
        
    def walk(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0
        
        v = 1.5        
        if inputState.isSet('run'): v = 2.5
        
        if inputState.isSet('forward'): speed.setY(v)
        if inputState.isSet('reverse'): speed.setY(-v)
        if inputState.isSet('left'):    speed.setX(-v)
        if inputState.isSet('right'):   speed.setX(v)
        
        if inputState.isSet('turnLeft'):  omega =  120.0
        if inputState.isSet('turnRight'): omega = -120.0

        self.controler.setAngularMovement(omega)
        self.controler.setLinearMovement(speed, True)  
        #print self.controler.isOnGround()  
        #self.controler.update()
