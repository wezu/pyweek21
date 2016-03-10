from panda3d.core import *
from toolkit import tex

MASK_SHADOW=BitMask32.bit(2)

class Grass():
    def __init__(self):
        self.node=render.attachNewNode('grass')
        self.createGrassTile(uv_offset=Vec2(0,0), pos=(0,0,0), parent=self.node, fogcenter=Vec3(256,256,0))
        self.createGrassTile(uv_offset=Vec2(0,0.5), pos=(0, 256, 0), parent=self.node, fogcenter=Vec3(256,0,0))
        self.createGrassTile(uv_offset=Vec2(0.5,0), pos=(256, 0, 0), parent=self.node, fogcenter=Vec3(0,256,0))
        self.createGrassTile(uv_offset=Vec2(0.5,0.5), pos=(256, 256, 0), parent=self.node, fogcenter=Vec3(0,0,0))
        self.node.setShaderInput('grass', loader.loadTexture(path+'data/red.png'))
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
        
        #ping-pong buffer         
        self.ping=None     
        self.pong=None
        self.mower=None
        self.time=0    
        self.state=0     
        self.update_speed=1.0/60.0         
        self.gradar=None
        self.pixel=None
        
    def update(self, task):        
        dt=globalClock.getDt()
        self.time+=dt
        if self.time>=self.update_speed:
            self.time=0            
            if self.state==0:            
                self.state=1                     
                self.ping['buff'].setActive(False)
                self.pong['buff'].setActive(True) 
                self.node.setShaderInput('cut', self.pong['tex'])
                self.gradar['quad'].setShaderInput('cut', self.pong['tex'])
                self.one_pixel['quad'].setShaderInput('cut',self.pong['tex'])
            else:
                self.state=0
                self.ping['buff'].setActive(True)
                self.pong['buff'].setActive(False) 
                self.node.setShaderInput('cut',self.ping['tex'])
                self.gradar['quad'].setShaderInput('cut', self.ping['tex'])
                self.one_pixel['quad'].setShaderInput('cut',self.ping['tex'])
        else:
            self.ping['buff'].setActive(False)
            self.pong['buff'].setActive(False)   
        return task.again
   
    def makeGradarBuffer(self, gradar_shader):
        root=NodePath("bufferRoot")
        tex=Texture()
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        tex.setMagfilter(Texture.FTLinearMipmapLinear)
        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        props = FrameBufferProperties()
        props.setRgbaBits(8, 8, 8, 8)
        props.setSrgbColor(False)  
        props.setFloatColor(False)      
        buff=base.win.makeTextureBuffer("buff", 128, 128, tex, fbp=props)
        buff.setClearColor(VBase4(0,0,0,0))
        #the camera for the buffer
        cam=base.makeCamera(win=buff)
        cam.reparentTo(root)          
        cam.setPos(256,256,100)                
        cam.setP(-90)                   
        lens = OrthographicLens()
        lens.setFilmSize(800, 800)  
        cam.node().setLens(lens)          
        #plane with the texture
        cm = CardMaker("plane")
        cm.setFrame(0, 512, 0, 512)        
        quad=root.attachNewNode(cm.generate())
        quad.lookAt(0, 0, -1)      
        quad.setAttrib(ShaderAttrib.make(gradar_shader))
        #return all the data in a dict
        return{'root':root, 'tex':tex, 'buff':buff, "cam":cam, 'quad':quad}    
   
        
        
    def makeBuffer(self, shader=None, size=512, texFilter=Texture.FTLinearMipmapLinear):
        root=NodePath("bufferRoot")
        tex=Texture()
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        tex.setMagfilter(texFilter)
        tex.setMinfilter(texFilter)
        props = FrameBufferProperties()
        props.setRgbaBits(8, 8, 8, 8)
        props.setSrgbColor(False)  
        props.setFloatColor(False)      
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
            quad.setAttrib(ShaderAttrib.make(shader))
        #return all the data in a dict
        return{'root':root, 'tex':tex, 'buff':buff, "cam":cam, 'quad':quad}    
   
    def setMap(self, texture):
        self.node.setShaderInput('grass', loader.loadTexture(texture))
        
        if self.ping is None:
            
            self.mower=self.makeBuffer(size=512)
            self.mower['quad'].setColor(0,0,0,1)
            cm = CardMaker("plane")
            cm.setFrame(-0.5, 0.5, -0.5, 0.5)        
            self.mower_blade=self.mower['root'].attachNewNode(cm.generate())
            self.mower_blade.lookAt(0, 0, -1)      
            self.mower_blade.setZ(10.0)
            self.mower_blade.setColor(1,0,0,1)
            self.mower_blade.hide()
            
            shader1=Shader.load(Shader.SL_GLSL,path+'shaders/mower_v.glsl', path+'shaders/mower_input_f.glsl')
            shader2=Shader.load(Shader.SL_GLSL,path+'shaders/mower_v.glsl', path+'shaders/mower_f.glsl')
        
            self.ping=self.makeBuffer(shader1)
            self.pong=self.makeBuffer(shader2)        
                      
            self.ping['quad'].setTexture(self.pong['tex'])
            self.pong['quad'].setTexture(self.ping['tex'])  
            self.ping['quad'].setShaderInput('startmap', self.mower['tex'])            
            self.ping['buff'].setActive(True)
            self.pong['buff'].setActive(False)     
            
            gradar_shader=Shader.load(Shader.SL_GLSL,path+'shaders/gradar_v.glsl', path+'shaders/gradar_f.glsl')
            self.gradar=self.makeGradarBuffer(gradar_shader)
            self.gradar['quad'].setShaderInput('mask', tex(path+'data/circle_mask.png'))
            self.gradar['quad'].setShaderInput('grass', tex(texture))           
            
            shader=Shader.load(Shader.SL_GLSL,path+'shaders/cut_count_v.glsl', path+'shaders/cut_count_f.glsl')
            self.one_pixel=self.makeBuffer(shader, size=128)
            self.one_pixel['quad'].setShaderInput('grass', tex(texture))
            
            
            taskMgr.add(self.update, 'update') 
    
    def setMowerPos(self, node):
        pos=node.getPos(render)
        h=node.getH(render)
        if self.ping:
            pos[2]=10.0
            self.mower_blade.setPos(pos)
            self.gradar['cam'].setPos(pos)
            self.gradar['cam'].setH(h)
            #self.gradar_hub.setH(-h)
            #pos[2]=0.0
            #self.gradar_hub.setPos(pos*0.25)  
              
    def getStatus(self):           
        p=PNMImage(128, 128,4)              
        base.graphicsEngine.extractTextureData(self.one_pixel['tex'],base.win.getGsg())
        self.one_pixel['tex'].store(p) 
        color=0
        #print p.getAverageGray()
        for x in xrange(128):
            for y in xrange(128):
                if p.getBright(x,y)>0.1:
                    color+=1
        return color         
        
    def createGrassTile(self, uv_offset, pos, parent, fogcenter=Vec3(0,0,0), count=256):
        grass=loader.loadModel(path+"data/grass_tiny")
        #grass.setTwoSided(True)
        grass.setTransparency(TransparencyAttrib.MBinary, 1)
        grass.reparentTo(parent)
        grass.setInstanceCount(count)
        grass.node().setBounds(BoundingBox((0,0,0), (256,256,128)))
        grass.node().setFinal(1)        
        grass.setShader(Shader.load(Shader.SLGLSL, path+"shaders/grass_v.glsl", path+"shaders/grass_f.glsl"))        
        grass.setShaderInput('uv_offset', uv_offset)
        grass.setShaderInput('fogcenter', fogcenter)
        grass.setShaderInput('pos', pos)
        render.setShaderInput('pc_pos', Vec3(0,0,0))
        grass.setPos(pos)
        return grass
