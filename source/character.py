from panda3d.core import *
from direct.showbase.InputStateGlobal import inputState
from direct.interval.IntervalGlobal import *
from panda3d.bullet import *
from direct.actor.Actor import Actor
from toolkit import *

class Character():
    def __init__(self, world, worldNP):
        self.flying_time=0.0
        radius = 0.3
        #shape = BulletSphereShape(radius)
        shape =BulletCapsuleShape(0.15, 0.6, ZUp)
        self.node = worldNP.attachNewNode(BulletRigidBodyNode('Sphere'))
        self.node.node().setMass(50.0)
        self.node.node().addShape(shape)        
        self.node.setCollideMask(BitMask32.allOn())
        self.node.node().setFriction(1.0)
        self.node.node().setAngularDamping(1.0)
        #self.node.node().setLinearDamping(0.5)
        self.node.node().setDeactivationEnabled(False)
        world.attachRigidBody(self.node.node())
    
        self.actor_node =render.attachNewNode('actor_node')    
        self.actor=Actor(path+'models/m_rocket',
                        {'walk':path+'models/a_rocket_walk1',
                        'run':path+'models/a_rocket_run',
                        'recover':path+'models/a_rocket_recover',
                        'drive':path+'models/a_rocket_drive',
                        'exit':path+'models/a_rocket_exit',
                        'jump':path+'models/a_rocket_jump2'}) 
        self.actor.loop('walk')                 
        self.actor.setScale(0.0128)
        self.actor.setH(180)
        self.actor.setZ(-0.45)
        self.actor.reparentTo(self.actor_node)  
        self.actor.setBlend(frameBlend = True)
        if cfg['hardware-skinning']:  
            attr = ShaderAttrib.make(Shader.load(Shader.SLGLSL, path+'shaders/actor_v.glsl', path+'shaders/default_f.glsl'))
            attr = attr.setFlag(ShaderAttrib.F_hardware_skinning, True)
            self.actor.setAttrib(attr)
        else:              
            self.actor.setShader(Shader.load(Shader.SLGLSL, path+'shaders/default_v.glsl', path+'shaders/default_f.glsl'))
        if cfg['srgb']: fixSrgbTextures(self.actor)
            
        self.world=world
        self.physic_node=self.node.node()
    
        self.last_know_ground_pos=self.node.getPos(render)

            
    
    def isOnGround(self):
        #print "ground test"
        result= self.world.contactTest(self.physic_node)   
        if result.getNumContacts()>0:
            for contact in result.getContacts():    
                n = contact.getManifoldPoint().getNormalWorldOnB()
                a = Vec3(0,0,1).angleDeg(Vec3(n)) 
                #print n
                if abs(a-180.0)<60.0 or a < 60.0:
                    self.last_know_ground_pos=self.node.getPos(render)
                    #print "on ground"
                    return True  
        #print "off ground"            
        return False
         
    def enterCar(self):
        self.hide()
    
    def exitCar(self, node):        
        pos=node.getPos(render)
        pos[2]+=1.2
        self.setPos(pos)
        Sequence(Wait(3.5), Func(self.show)).start()
        self.physic_node.setLinearVelocity(Vec3(0,0,0))
        
    def hide(self):
        self.actor.hide()
        self.world.remove(self.node.node())
    
    def show(self):
        self.actor.show()
        self.world.attach(self.node.node())
        self.physic_node.setLinearVelocity(Vec3(0,0,0)) 
        
    def setPos(self, *args):
        pos=[]
        for arg in args:
            pos.append(arg)
        if len(pos)==1:                
            self.node.setPos(render, pos[0])
        elif len(pos)>2:        
            self.node.setPos(render, Vec3(pos[0],pos[1],pos[2]))
        self.actor_node.setPos(self.node.getPos(render))
            
    def jump(self):
        if self.isOnGround():
            force = self.actor_node.getRelativeVector(render, self.physic_node.getLinearVelocity())*1000.0
            #print force   
            force += Vec3(0, 0, 20000.0)
            force = render.getRelativeVector(self.actor_node, force)
            self.physic_node.applyCentralForce(force)
            self.actor.play('jump')
        
    def walk(self, dt):
        self.node.setHpr(0,0,0)
        self.actor_node.setPos(self.node.getPos(render))
        speed= self.actor_node.getRelativeVector(render, self.physic_node.getLinearVelocity())
        speed_co=1.05-max(0.01, abs(speed.y))/8.0
        #print speed_co
        force = Vec3(0, 0, 0.0)
        if self.flying_time>0.4 and self.actor.getCurrentAnim()!='jump':
            self.actor.pose('jump', 20)
        if self.flying_time>2.0:
            print "reset!"
            #self.node.node().setMass(0.0)
            self.node.setPos(self.last_know_ground_pos)
            self.node.setZ(self.node.getZ(render)+1.0)
            self.node.setY(self.node.getY(render)+1.0)
            self.physic_node.setLinearVelocity(Vec3(0,0,0))
            self.flying_time=0.0
            return       
        if self.isOnGround():
            if self.flying_time> 0.8:
                self.actor.play('recover')
                self.physic_node.setLinearVelocity(Vec3(0,0,0))  
            self.flying_time=0.0            
            if self.actor.getCurrentAnim() not in ('jump', 'recover'):
                if speed.y>4.0:
                    if self.actor.getCurrentAnim()!= 'run':
                        self.actor.loop('run')
                    self.actor.setPlayRate((speed.y*0.5)-1.0,'run')
                else:   
                    if self.actor.getCurrentAnim()!= 'walk':
                        self.actor.loop('walk')  
                    self.actor.setPlayRate((speed.y*0.8),'walk')            
            if self.actor.getCurrentAnim()!='recover':                             
                #if inputState.isSet('run'): v = 75 *dt            
                if inputState.isSet('forward'):
                    force.setY(60000.0*dt*speed_co) 
                if inputState.isSet('reverse'):
                    force.setY(-40000.0*dt*speed_co)
                if inputState.isSet('turnLeft'):
                    self.actor_node.setH(self.actor_node, 90.0*dt)
                if inputState.isSet('turnRight'):
                    self.actor_node.setH(self.actor_node, -90.0*dt)

                #if force.getY()==0.0:
                #    self.physic_node.setLinearVelocity(speed*0.5)                                           
        else:
            self.flying_time+=dt    
            if inputState.isSet('forward'):
                force.setY(10000.0*dt) 
            if inputState.isSet('reverse'):
                force.setY(-10000.0*dt)
            if inputState.isSet('turnLeft'):
                force.setX(-10000.0*dt)
            if inputState.isSet('turnRight'):
                force.setX(10000.0*dt)
        force = render.getRelativeVector(self.actor_node, force)    
        self.physic_node.applyCentralForce(force) 
