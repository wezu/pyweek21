from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.bullet import *
from toolkit import *

class Car():
    def __init__(self,
                world,
                worldNP,
                box=Vec3(0.25, 0.9, 0.3),
                shape_offset=Point3(0, 0.25, 0.4),
                mass=300.0,
                chassis='models/car_chassis',
                wheel='models/wheel1',
                wheel_pos=[Point3(0.35, 0.83, 0.35),Point3(-0.35, 0.83, 0.35),Point3( 0.35, -0.32, 0.35),Point3(-0.35, -0.32, 0.35)],
                ):
        self.mass=mass  
        self.worldNP=worldNP
        self.world=world
        # Chassis
        shape = BulletBoxShape(box)        
        ts = TransformState.makePos(shape_offset)

        self.node = worldNP.attachNewNode(BulletRigidBodyNode('Vehicle'))
        self.node.node().addShape(shape, ts)
        self.node.setPos(0, 0, 1)
        self.node.node().setMass(mass)
        self.node.node().setDeactivationEnabled(False)

        world.attachRigidBody(self.node.node())

        # Vehicle
        self.vehicle = BulletVehicle(world, self.node.node())
        self.vehicle.setCoordinateSystem(ZUp)
        world.attach(self.vehicle)
        
        #visible part
        self.model = loader.loadModel(chassis)
        self.model.reparentTo(self.node)
        self.model.setShader(Shader.load(Shader.SLGLSL, 'shaders/default_v.glsl', 'shaders/default_f.glsl'))
        if cfg['srgb']: fixSrgbTextures(self.model)
        
        # Right front wheel
        self.addWheel(wheel_pos[0], True, wheel)
        # Left front wheel
        self.addWheel(wheel_pos[1], True, wheel)
        # Right rear wheel
        self.addWheel(wheel_pos[2], False, wheel)
        # Left rear wheel
        self.addWheel(wheel_pos[3], False, wheel)

        # Steering info
        self.steering = 0.0           
        self.engine_force=0.0
        self.steering_clamp = 30.0      
        self.steering_increment = 0.6                 
    
        #sfx
        self.sfx={}
        self.sfx['engine']=loader.loadSfx("sfx/engine2.ogg")
        self.sfx['engine'].setLoop(True)
        self.sfx['brum']=loader.loadSfx("sfx/brum2.ogg")
        self.sfx['skid']=loader.loadSfx("sfx/break3.ogg")
        self.sfx['skid_start']=loader.loadSfx("sfx/break_start.ogg")
        self.sfx['engine_start']=loader.loadSfx("sfx/engine_start.ogg")
        self.sfx['springs']=loader.loadSfx("sfx/springs.ogg")
        #self.sfx['crash1']=loader.loadSfx("sfx/crash1.ogg")
        #self.sfx['crash2']=loader.loadSfx("sfx/crash2.ogg")
        #self.sfx['crash3']=loader.loadSfx("sfx/crash3.ogg")
        #self.sfx['crash4']=loader.loadSfx("sfx/crash4.ogg")
        self.sfx['crash5']=loader.loadSfx("sfx/crash5.ogg")
        self.sfx['crash6']=loader.loadSfx("sfx/crash6.ogg")
                
        for sound in self.sfx:            
            self.sfx[sound].setVolume(0.5)
            
        self.isEngineRunning=False
        
    def isSfxPlaying(self, name):
        if self.sfx[name].status() == AudioSound.PLAYING:
            return True
        return False
    
    def playSfx(self, name, play_rate=1.0):
        self.sfx[name].setPlayRate(play_rate)
        if not self.isSfxPlaying(name):
            self.sfx[name].play()
            
    def stopSfx(self, name):
        self.sfx[name].stop()
    
    def setHandBreak(self):
        #this work's not! (???)
        self.brake_force=10000.0
        self.engine_force=0.0
        self.vehicle.setBrake(self.brake_force, 0)
        self.vehicle.setBrake(self.brake_force, 1)
        self.vehicle.setBrake(self.brake_force, 2)
        self.vehicle.setBrake(self.brake_force, 3)
        self.vehicle.applyEngineForce(self.engine_force, 0)
        self.vehicle.applyEngineForce(self.engine_force, 1)
        # Apply engine and brake to rear wheels
        self.vehicle.applyEngineForce(self.engine_force, 2)
        self.vehicle.applyEngineForce(self.engine_force, 3)
        self.vehicle.setSteeringValue(0.0, 0)
        self.vehicle.setSteeringValue(0.0, 1)
        
    def _setEngineRunning(self, value):
        self.isEngineRunning=value
        if value==True:
            self.node.node().setMass(self.mass)
            self.brake_force=0.0
            self.vehicle.setBrake(self.brake_force, 0)
            self.vehicle.setBrake(self.brake_force, 1)
            self.vehicle.setBrake(self.brake_force, 2)
            self.vehicle.setBrake(self.brake_force, 3)
        
    def startEngine(self):
        if not self.isSfxPlaying('engine_start'):
            Sequence(
                    Func(self.sfx['engine_start'].play),
                    Wait(1.0), Func(self.sfx['engine'].play),
                    Func(self._setEngineRunning,True)
                    ).start()
        
        
    def stopEngine(self):
        if self.vehicle.getCurrentSpeedKmHour()<1.0:            
            self.sfx['engine'].stop()         
            self.isEngineRunning=False
            self.brake_force=10000.0
            self.vehicle.setBrake(self.brake_force, 0)
            self.vehicle.setBrake(self.brake_force, 1)
            self.vehicle.setBrake(self.brake_force, 2)
            self.vehicle.setBrake(self.brake_force, 3)        
            self.node.node().setMass(0)
            return True
        return False    
        
    def addWheel(self, pos, front, model):
        np = loader.loadModel(model)
        np.reparentTo(self.worldNP)
        if cfg['srgb']: fixSrgbTextures(np)
        np.setShader(Shader.load(Shader.SLGLSL, 'shaders/default_v.glsl', 'shaders/default_f.glsl'))
        wheel = self.vehicle.createWheel()
        wheel.setNode(np.node())
        wheel.setChassisConnectionPointCs(pos)
        wheel.setFrontWheel(front)
        wheel.setWheelDirectionCs(Vec3(0, 0, -1))
        wheel.setWheelAxleCs(Vec3(1, 0, 0))
        wheel.setWheelRadius(0.21)
        wheel.setMaxSuspensionTravelCm(20.0)
        wheel.setSuspensionStiffness(60.0)
        wheel.setWheelsDampingRelaxation(2.0) #def 2.3
        wheel.setWheelsDampingCompression(2.0) #def 4.4 min 0.1 max 10.0
        wheel.setFrictionSlip(150.0); #max 5.0 min 1.2
        wheel.setRollInfluence(0.01)
    
    def drive(self, dt):
        is_trurning=False          
        suspension_force=0
        rate=1.0
        for wheel in self.vehicle.getWheels():
            suspension_force+=wheel.getWheelsSuspensionForce()         
        if suspension_force == float('Inf'):
            suspension_force=0.0    
        if suspension_force>4000:
            self.playSfx('springs',rate)
        if suspension_force>5000:
            self.playSfx('crash6',rate)
        if suspension_force>8000:
            self.playSfx('crash5',rate)              
        speed_coef=max(1.0,(100.0-self.vehicle.getCurrentSpeedKmHour()))
        
        if inputState.isSet('forward'):
            if not self.isEngineRunning:
                self.startEngine()
                return            
            if self.engine_force == 0.0:
                self.playSfx('brum')
            self.engine_force=speed_coef*1000.0*dt          
            self.brake_force = 0.0
            rpm= (900.0-self.engine_force)/900.0
        else:
            self.engine_force=0
            rpm= (900.0-(speed_coef*1000.0*dt))/900.0
              
        if inputState.isSet('reverse'):
            self.engine_force = 0.0                        
            if (
                self.vehicle.getCurrentSpeedKmHour()>20.0 and
                self.brake_force == 0.0 and 
                (self.vehicle.getWheel(2).getRaycastInfo().isInContact() or
                self.vehicle.getWheel(3).getRaycastInfo().isInContact()) and
                not self.isSfxPlaying('skid_start')                     
                ): 
                tempo=1.5-self.vehicle.getCurrentSpeedKmHour()/100.0
                self.playSfx('skid_start', tempo)
                self.playSfx('skid', tempo)
            self.brake_force = 10.0
        else:
            self.brake_force = 0.0
            if self.isSfxPlaying('skid') :
                self.stopSfx('skid')            
        if inputState.isSet('turnLeft'):
            self.steering += dt * self.steering_increment*(speed_coef+10.0)
            self.steering = min(self.steering, self.steering_clamp)
            is_trurning=True
        if inputState.isSet('turnRight'):
            self.steering -= dt * self.steering_increment*(speed_coef+10.0)
            self.steering = max(self.steering, -self.steering_clamp)
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
        rpm*=rpm     
        self.sfx['engine'].setPlayRate(0.8+rpm)        
        self.sfx['engine'].setVolume(0.3+rpm)
        
        # Apply steering to front wheels
        self.vehicle.setSteeringValue(self.steering, 0)
        self.vehicle.setSteeringValue(self.steering, 1)
        # Apply engine and brake to front wheels
        self.vehicle.applyEngineForce(self.engine_force, 0)
        self.vehicle.applyEngineForce(self.engine_force, 1)
        # Apply engine and brake to rear wheels
        self.vehicle.applyEngineForce(self.engine_force, 2)
        self.vehicle.applyEngineForce(self.engine_force, 3)        
        self.vehicle.setBrake(self.brake_force, 2)
        self.vehicle.setBrake(self.brake_force, 3)
        
    def setPos(self, *args):
        pos=[]
        for arg in args:
            pos.append(arg)
        if len(pos)==1:                
            self.node.setPos(render, pos)
        elif len(pos)>2:        
            self.node.setPos(render, Vec3(pos[0],pos[1],pos[2]))
        
    def flip(self):
        if abs(self.node.getR(render))>90.0 and self.vehicle.getCurrentSpeedKmHour() <= 1.0:
            self.node.setZ(self.node.getZ()+1.5)
            self.node.setR(render, 0.0)
