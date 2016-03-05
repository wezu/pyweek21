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
        shape = BulletSphereShape(radius)
        self.node = worldNP.attachNewNode(BulletRigidBodyNode('Sphere'))
        self.node.node().setMass(50.0)
        self.node.node().addShape(shape)        
        self.node.setCollideMask(BitMask32.allOn())
        self.node.node().setFriction(1.0)
        self.node.node().setAngularDamping(0.999)
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
                        'jump':path+'models/a_rocket_jump'}) 
        self.actor.loop('walk')                 
        self.actor.setScale(0.0128)
        self.actor.setH(180)
        self.actor.setZ(-radius)
        self.actor.reparentTo(self.actor_node)  
        self.actor.setBlend(frameBlend = True)
        if cfg['hardware-skinning']:  
            attr = ShaderAttrib.make(Shader.load(Shader.SLGLSL, 'shaders/actor_v.glsl', 'shaders/default_f.glsl'))
            attr = attr.setFlag(ShaderAttrib.F_hardware_skinning, True)
            self.actor.setAttrib(attr)
        else:              
            self.actor.setShader(Shader.load(Shader.SLGLSL, 'shaders/default_v.glsl', 'shaders/default_f.glsl'))
        if cfg['srgb']: fixSrgbTextures(self.actor)
            
        self.world=world
        self.physic_node=self.node.node()
    
    def enterCar(self):
        self.hide()
    
    def _enableControl(self, node):
        pos=node.getPos(render)
        #pos[1]+=0.155712
        pos[2]+=1.2
        self.node.setPos(render, pos)     
        self.actor.reparentTo(self.actor_node)    
        self.actor.setZ(-0.31)    
        self.world.attach(self.node.node())
        self.physic_node.setLinearVelocity(Vec3(0,0,0))    
    
    def exitCar(self, node):        
        pos=node.getPos(render)
        pos[2]+=1
        self.setPos(pos)
        Sequence(Wait(3.5), Func(self.show)).start()
        
    def hide(self):
        self.actor.hide()
        self.world.remove(self.node.node())
    
    def show(self):
        self.actor.show()
        self.world.attach(self.node.node())
         
        
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
        if self.world.contactTest(self.physic_node).getNumContacts()>0: 
            force = self.actor_node.getRelativeVector(render, self.physic_node.getLinearVelocity())*1000.0 
            #print force
            force += Vec3(0, 0, 20000.0)
            force = render.getRelativeVector(self.actor_node, force)
            self.physic_node.applyCentralForce(force)
            self.actor.play('jump')
        
    def walk(self, dt):
        self.actor_node.setPos(self.node.getPos(render))
        speed= self.actor_node.getRelativeVector(render, self.physic_node.getLinearVelocity())
        speed_co=max(0.1,1.0-max(0.01, speed.y)/8.0)
        if self.flying_time>0.4 and self.actor.getCurrentAnim()!='jump':
            self.actor.pose('jump', 12)
        if self.world.contactTest(self.physic_node).getNumContacts()>0:
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
                force = Vec3(0, 0, 0.0)             
                #if inputState.isSet('run'): v = 75 *dt            
                if inputState.isSet('forward'):
                    force.setY(80000.0*dt*speed_co)        
                if inputState.isSet('reverse'):
                    force.setY(-80000.0*dt*speed_co)
                if inputState.isSet('turnLeft'):
                    self.actor_node.setH(self.actor_node, 90.0*dt)
                if inputState.isSet('turnRight'):
                    self.actor_node.setH(self.actor_node, -90.0*dt)

                if force.getY()==0.0:
                    self.physic_node.setLinearVelocity(speed*0.5)
                
                force = render.getRelativeVector(self.actor_node, force)    
                self.physic_node.applyCentralForce(force)            
        else:
            self.flying_time+=dt    
        
