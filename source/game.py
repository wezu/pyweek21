import sys

from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

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
    base.cam.setPos(0, -8, 3)
    base.cam.lookAt(0, 3, 1)    
    
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
    base.camera.wrtReparentTo(self.yugoNP)
    
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
    brakeForce = 0.0
    is_trurning=False
    speed_co=max(1.0,(100.0-self.vehicle.getCurrentSpeedKmHour()))
    #print speed_co
    
    if inputState.isSet('forward'):
        self.engineForce += dt*speed_co*20.0
        brakeForce = 0.0
    else:
        self.engineForce =0
      
    if inputState.isSet('reverse'):
        self.engineForce = 0.0
        brakeForce = 10.0

    if inputState.isSet('turnLeft'):
        self.steering += dt * self.steeringIncrement*(speed_co+10.0)
        self.steering = min(self.steering, self.steeringClamp)
        is_trurning=True

    if inputState.isSet('turnRight'):
        self.steering -= dt * self.steeringIncrement*(speed_co+10.0)
        self.steering = max(self.steering, -self.steeringClamp)
        is_trurning=True
      
    if not is_trurning:
        if self.steering >0:
            self.steering-=dt*30.0
        else:        
            self.steering+=dt*30.0
        if abs(self.steering)<0.1:
            self.steering=0.0
            
    if self.engineForce >5000.0:
        self.engineForce=5000.0
    if self.engineForce <0.0:
        self.engineForce=0.0
    if self.vehicle.getCurrentSpeedKmHour()>150.0:
        self.engineForce=0.0   
    # Apply steering to front wheels
    self.vehicle.setSteeringValue(self.steering, 0);
    self.vehicle.setSteeringValue(self.steering, 1);

    # Apply engine and brake to rear wheels
    self.vehicle.applyEngineForce(self.engineForce, 2);
    self.vehicle.applyEngineForce(self.engineForce, 3);
    self.vehicle.setBrake(brakeForce, 2);
    self.vehicle.setBrake(brakeForce, 3);

  def update(self, task):
    dt = globalClock.getDt()

    self.processInput(dt)
    self.world.doPhysics(dt, 10, 0.001)

    #print self.vehicle.getWheel(0).getRaycastInfo().isInContact()
    #print self.vehicle.getWheel(0).getRaycastInfo().getContactPointWs()

    #print self.vehicle.getChassis().isKinematic()
    #print self.vehicle.getCurrentSpeedKmHour()
    
    return task.cont

  def cleanup(self):
    self.world = None
    self.worldNP.removeNode()

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

    np = self.worldNP.attachNewNode(BulletRigidBodyNode('Vehicle'))
    np.node().addShape(shape, ts)
    np.setPos(0, 0, 1)
    np.node().setMass(800.0)
    np.node().setDeactivationEnabled(False)

    self.world.attachRigidBody(np.node())

    #np.node().setCcdSweptSphereRadius(1.0)
    #np.node().setCcdMotionThreshold(1e-7) 

    # Vehicle
    self.vehicle = BulletVehicle(self.world, np.node())
    self.vehicle.setCoordinateSystem(ZUp)
    self.world.attachVehicle(self.vehicle)

    self.yugoNP = loader.loadModel('models/car_chassis.egg')
    self.yugoNP.reparentTo(np)

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
    self.steeringClamp = 45.0      # degree
    self.steeringIncrement = 0.6 # degree per second
    self.engineForce=0.0
    
  def addWheel(self, pos, front, np):
    wheel = self.vehicle.createWheel()

    wheel.setNode(np.node())
    wheel.setChassisConnectionPointCs(pos)
    wheel.setFrontWheel(front)

    wheel.setWheelDirectionCs(Vec3(0, 0, -1))
    wheel.setWheelAxleCs(Vec3(1, 0, 0))
    wheel.setWheelRadius(0.21)
    wheel.setMaxSuspensionTravelCm(20.0)

    
    wheel.setSuspensionStiffness(50.0)
    wheel.setWheelsDampingRelaxation(2.3) #def 2.3
    wheel.setWheelsDampingCompression(4.4) #def 4.4 min 0.1 max 10.0
    wheel.setFrictionSlip(15.0); #max 5.0 min 1.2
    wheel.setRollInfluence(0.002)



