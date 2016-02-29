import sys

from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.bullet import *

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


        # Input
        self.accept('escape', self.doExit)
        self.accept('r', self.doReset)
        self.accept('f1', self.toggleWireframe)
        self.accept('f2', self.toggleTexture)
        self.accept('f3', self.toggleDebug)
        self.accept('f5', self.doScreenshot)
        self.accept('space', self.doFlip)

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

    def processInput(self, dt):               
        is_trurning=False
        
        speed_co=max(1.0,(100.0-self.vehicle.getCurrentSpeedKmHour()))
        #print speed_co        
        
        if inputState.isSet('forward'):
            if self.engineForce == 0.0 and self.engine_brum.status() != self.engine_brum.PLAYING:                
                self.engine_brum.play()
            self.engineForce=speed_co*1000.0*dt          
            self.brakeForce = 0.0
            rpm= (900.0-self.engineForce)/900.0
            #print self.engineForce            
        else:
            self.engineForce=0
            rpm= (900.0-(speed_co*1000.0*dt))/900.0
              
        if inputState.isSet('reverse'):
            self.engineForce = 0.0            
            if self.vehicle.getCurrentSpeedKmHour()>20.0:                
                if ( self.brakeForce == 0.0 and 
                    (self.vehicle.getWheel(2).getRaycastInfo().isInContact() or
                     self.vehicle.getWheel(3).getRaycastInfo().isInContact()) and
                     self.break_sound1.status() != self.break_sound1.PLAYING
                    ): 
                    tempo=1.5-self.vehicle.getCurrentSpeedKmHour()/100.0
                    self.break_sound1.setPlayRate(tempo) 
                    self.break_sound2.setPlayRate(tempo) 
                    self.break_sound1.play()
                    self.break_sound2.play()
            self.brakeForce = 10.0
        else:
            self.brakeForce = 0.0
            if self.break_sound1.status() == self.break_sound1.PLAYING:
                self.break_sound1.stop()
            
        if inputState.isSet('turnLeft'):
            self.steering += dt * self.steeringIncrement*(speed_co+10.0)
            self.steering = min(self.steering, self.steeringClamp)
            is_trurning=True

        if inputState.isSet('turnRight'):
            self.steering -= dt * self.steeringIncrement*(speed_co+10.0)
            self.steering = max(self.steering, -self.steeringClamp)
            is_trurning=True
          
        if not is_trurning:
            if abs(self.steering) >0:
                self.steering*=0.8            
            if abs(self.steering)<1.0:
                self.steering=0.0
               
        #play sfx  
        if rpm==1.0:
            rpm=0.0
        if rpm<0.0:
            rpm=0.0
        self.engine_sound.setPlayRate(0.8+rpm*0.4)        
        
        # Apply steering to front wheels
        self.vehicle.setSteeringValue(self.steering, 0)
        self.vehicle.setSteeringValue(self.steering, 1)

        # Apply engine and brake to front wheels
        self.vehicle.applyEngineForce(self.engineForce, 0)
        self.vehicle.applyEngineForce(self.engineForce, 1)
        # Apply engine and brake to rear wheels
        self.vehicle.applyEngineForce(self.engineForce, 2)
        self.vehicle.applyEngineForce(self.engineForce, 3)
        
        self.vehicle.setBrake(self.brakeForce, 2)
        self.vehicle.setBrake(self.brakeForce, 3)

    def update(self, task):
        dt = globalClock.getDt()

        self.processInput(dt)
        self.world.doPhysics(dt, 10, 0.001)
        self.cameraRotation(dt)
        
        #print self.vehicle.getWheel(0).getRaycastInfo().isInContact()
        #print self.vehicle.getWheel(0).getRaycastInfo().getContactPointWs()

        #print self.vehicle.getChassis().isKinematic()
        #print self.vehicle.getCurrentSpeedKmHour()
    
        return task.cont

    def cleanup(self):
        self.world = None
        self.worldNP.removeNode()
        
    def doFlip(self):
        test=self.vehicle.getWheel(0).getRaycastInfo().isInContact()
        test+=self.vehicle.getWheel(1).getRaycastInfo().isInContact()
        test+=self.vehicle.getWheel(2).getRaycastInfo().isInContact()
        test+=self.vehicle.getWheel(3).getRaycastInfo().isInContact()
        print test
        self.vehicle_np.setZ(3.0)
    
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

        # Chassis
        shape = BulletBoxShape(Vec3(0.5*0.5, 1.8*0.5, 0.6*0.5))
        ts = TransformState.makePos(Point3(0, 0.25, 0.4))

        self.vehicle_np = self.worldNP.attachNewNode(BulletRigidBodyNode('Vehicle'))
        self.vehicle_np.node().addShape(shape, ts)
        self.vehicle_np.setPos(0, 0, 1)
        self.vehicle_np.node().setMass(300.0)
        self.vehicle_np.node().setDeactivationEnabled(False)

        self.world.attachRigidBody(self.vehicle_np.node())

        #np.node().setCcdSweptSphereRadius(1.0)
        #np.node().setCcdMotionThreshold(1e-7) 

        # Vehicle
        self.vehicle = BulletVehicle(self.world, self.vehicle_np.node())
        self.vehicle.setCoordinateSystem(ZUp)
        self.world.attachVehicle(self.vehicle)

        self.yugoNP = loader.loadModel('models/car_chassis.egg')
        self.yugoNP.reparentTo(self.vehicle_np)

        # Right front wheel
        np = loader.loadModel('models/wheel1.egg')
        np.reparentTo(self.worldNP)
        self.addWheel(Point3(0.35, 0.83, 0.35), True, np)

        # Left front wheel
        np = loader.loadModel('models/wheel1.egg')
        np.reparentTo(self.worldNP)
        self.addWheel(Point3(-0.35, 0.83, 0.35), True, np)

        # Right rear wheel
        np = loader.loadModel('models/wheel1.egg')
        np.reparentTo(self.worldNP)
        self.addWheel(Point3( 0.35, -0.32, 0.35), False, np)

        # Left rear wheel
        np = loader.loadModel('models/wheel1.egg')
        np.reparentTo(self.worldNP)
        self.addWheel(Point3(-0.35, -0.32, 0.35), False, np)

        # Steering info
        self.steering = 0.0            # degree
        self.steeringClamp = 30.0      # degree
        self.steeringIncrement = 0.6 # degree per second
        self.engineForce=0.0
        #camera
        self.cam_node=render.attachNewNode("cam_node")
        base.cam.reparentTo(self.cam_node)
        base.cam.setPos(0, -5, 1.8)
        base.cam.setP(-10)
    
        #sfx
        self.engine_sound=loader.loadSfx("sfx/engine2.ogg")
        self.engine_sound.setLoop(True)
        self.engine_sound.play()
        self.engine_brum=loader.loadSfx("sfx/brum2.ogg")
        self.break_sound1=loader.loadSfx("sfx/break3.ogg")
        self.break_sound2=loader.loadSfx("sfx/break_start.ogg")
        
    def cameraRotation(self, dt):
        self.cam_node.setPos(self.yugoNP.getPos(render))        
        orig_H = self.cam_node.getH(render)
        target_H = self.yugoNP.getH(render)
        # Make the rotation go the shortest way around.
        origH = fitSrcAngle2Dest(orig_H, target_H)

        # How far do we have to go from here?
        delta = abs(target_H - orig_H)
        if delta == 0:
            # We're already looking at the target.
            return
        # Figure out how far we should rotate in this frame, based on the
        # distance to go, and the speed we should move each frame.
        t = dt * delta *0.3
        # If we reach the target, stop there.
        t = min(t, 1.0)
        new_H = orig_H + (target_H - orig_H) * t
        self.cam_node.setH(new_H)
        
    
    
    def addWheel(self, pos, front, np):
        wheel = self.vehicle.createWheel()

        wheel.setNode(np.node())
        wheel.setChassisConnectionPointCs(pos)
        wheel.setFrontWheel(front)

        wheel.setWheelDirectionCs(Vec3(0, 0, -1))
        wheel.setWheelAxleCs(Vec3(1, 0, 0))
        wheel.setWheelRadius(0.21)
        wheel.setMaxSuspensionTravelCm(20.0)

        
        wheel.setSuspensionStiffness(40.0)
        wheel.setWheelsDampingRelaxation(2.0) #def 2.3
        wheel.setWheelsDampingCompression(2.0) #def 4.4 min 0.1 max 10.0
        wheel.setFrictionSlip(150.0); #max 5.0 min 1.2
        wheel.setRollInfluence(0.01)



