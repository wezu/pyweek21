from panda3d.core import *

MASK_SHADOW=BitMask32.bit(2)

class Grass():
    def __init__(self):
        self.node=render.attachNewNode('grass')
        self.createGrassTile(uv_offset=Vec2(0,0), pos=(0,0,0), parent=self.node, fogcenter=Vec3(256,256,0))
        self.createGrassTile(uv_offset=Vec2(0,0.5), pos=(0, 256, 0), parent=self.node, fogcenter=Vec3(256,0,0))
        self.createGrassTile(uv_offset=Vec2(0.5,0), pos=(256, 0, 0), parent=self.node, fogcenter=Vec3(0,256,0))
        self.createGrassTile(uv_offset=Vec2(0.5,0.5), pos=(256, 256, 0), parent=self.node, fogcenter=Vec3(0,0,0))
        self.node.setBin("background", 11)
        self.node.hide(MASK_SHADOW)

        grass_tex0=loader.loadTexture(path+'grass_tex/11.png')
        grass_tex0.setWrapU(Texture.WMClamp)
        grass_tex0.setWrapV(Texture.WMClamp)
        grass_tex0.setMinfilter(Texture.FTLinearMipmapLinear)
        grass_tex0.setMagfilter(Texture.FTLinear)
        if cfg['srgb']: grass_tex0.setFormat(Texture.F_srgb_alpha)
        
        grass_tex1=loader.loadTexture(path+'grass_tex/12.png')
        grass_tex1.setWrapU(Texture.WMClamp)
        grass_tex1.setWrapV(Texture.WMClamp)
        grass_tex1.setMinfilter(Texture.FTLinearMipmapLinear)
        grass_tex1.setMagfilter(Texture.FTLinear)
        if cfg['srgb']: grass_tex1.setFormat(Texture.F_srgb_alpha)
        
        grass_tex2=loader.loadTexture(path+'grass_tex/13.png')
        grass_tex2.setWrapU(Texture.WMClamp)
        grass_tex2.setWrapV(Texture.WMClamp)
        grass_tex2.setMinfilter(Texture.FTLinearMipmapLinear)
        grass_tex2.setMagfilter(Texture.FTLinear)
        if cfg['srgb']: grass_tex2.setFormat(Texture.F_srgb_alpha)
        
        
        self.node.setShaderInput('tex1', grass_tex0)
        self.node.setShaderInput('tex2', grass_tex1)
        self.node.setShaderInput('tex3', grass_tex2)       
        
        #make the ping-pong buffer
        #shader1=Shader.load(Shader.SL_GLSL,'v.glsl', 'make_wave_f.glsl')
        #shader2=Shader.load(Shader.SL_GLSL,'v.glsl', 'make_wave2_f.glsl')        
        #self.ping=self.makeBuffer(shader1, size)
        #self.pong=self.makeBuffer(shader2, size)
        #self.ping['quad'].setShaderInput("size",float(size))
        #self.pong['quad'].setShaderInput("size",float(size))        
        #self.ping['quad'].setTexture(self.pong['tex'])
        #self.pong['quad'].setTexture(self.ping['tex'])        
        #self.ping['quad'].setShaderInput('startmap', self.wave_source['tex'])        
        #self.ping['buff'].setActive(True)
        #self.pong['buff'].setActive(False)

        #update task
        #taskMgr.add(self.update, 'update') 
        
    def update(self, task):        
        dt=globalClock.getDt()
        self.time+=dt
        if self.time>=self.update_speed:
            self.time=0            
            if self.state==0:            
                self.state=1            
                self.ping['buff'].setActive(False)
                self.pong['buff'].setActive(True)    
                self.plane.setTexture(self.pong['tex']) 
            else:
                self.state=0
                self.ping['buff'].setActive(True)
                self.pong['buff'].setActive(False)             
                self.plane.setTexture(self.ping['tex'])           
        else:
            self.ping['buff'].setActive(False)
            self.pong['buff'].setActive(False) 
        return task.again
   
    def makeBuffer(self, shader=None, size=256, texFilter=Texture.FTLinearMipmapLinear):
        root=NodePath("bufferRoot")
        tex=Texture()
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        tex.setMagfilter(texFilter)
        tex.setMinfilter(texFilter)
        props = FrameBufferProperties()
        props.setRgbaBits(16, 16, 0, 0)
        props.setSrgbColor(False)  
        props.setFloatColor(True)      
        buff=base.win.makeTextureBuffer("buff", size, size, tex, fbp=props)
        #the camera for the buffer
        cam=base.makeCamera(win=buff)
        cam.reparentTo(root)          
        cam.setPos(size/2,size/2,100)                
        cam.setP(-90)                   
        lens = OrthographicLens()
        lens.setFilmSize(size, size)  
        cam.node().setLens(lens)          
        #plane with the texture
        cm = CardMaker("plane")
        cm.setFrame(0, size, 0, size)        
        quad=root.attachNewNode(cm.generate())
        quad.lookAt(0, 0, -1)      
        if shader:
            ShaderAttrib.make(shader)  
            quad.setAttrib(ShaderAttrib.make(shader))
        #return all the data in a dict
        return{'root':root, 'tex':tex, 'buff':buff, "cam":cam, 'quad':quad}    
   
    def setGrassMap(self, texture):
        pass

    def createGrassTile(self, uv_offset, pos, parent, fogcenter=Vec3(0,0,0), count=256):
        grass=loader.loadModel(path+"data/grass_tiny")
        #grass.setTwoSided(True)
        grass.setTransparency(TransparencyAttrib.MBinary, 1)
        grass.reparentTo(parent)
        grass.setInstanceCount(count)
        grass.node().setBounds(BoundingBox((0,0,0), (256,256,128)))
        grass.node().setFinal(1)        
        grass.setShader(Shader.load(Shader.SLGLSL, path+"shaders/grass_v.glsl", path+"shaders/grass_f.glsl"))
        grass.setShaderInput('grass', loader.loadTexture(path+'data/red.png'))
        grass.setShaderInput('uv_offset', uv_offset)
        grass.setShaderInput('fogcenter', fogcenter)
        grass.setShaderInput('pos', pos)
        render.setShaderInput('pc_pos', Vec3(0,0,0))
        grass.setPos(pos)
        return grass
