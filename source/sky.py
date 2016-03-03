from panda3d.core import *
from light_manager import LightManager

MASK_SHADOW=BitMask32.bit(2)

class Sky():
    def __init__(self):
        self.skyimg=PNMImage(path+'data/sky_color.png')
        #if cfg['srgb']: self.skyimg.setColorSpace(CS_scRGB) 
        self.skydome = loader.loadModel(path+'data/skydome')
        tex = loader.loadTexture('data/clouds.png')
        if cfg['srgb']:tex.setFormat(Texture.F_srgb_alpha)
        self.skydome.setTexture(tex, 1) 
        self.skydome.reparentTo(render)
        self.skydome.setPos(256, 256, -200)
        self.skydome.setScale(10)
        #self.skydome.setShaderInput("fog", Vec4(1.0,1.0,1.0, 1.0))
        #self.skydome.setShaderInput("cloudColor", Vec4(0.9,0.9,1.0, 0.8))
        self.skydome.setShaderInput("cloudTile",8.0)
        self.skydome.setShaderInput("cloudSpeed",0.008)
        #self.skydome.setShaderInput("sunColor",Vec4(1.0,1.0,1.0, 1.0))
        #self.skydome.setShaderInput("skyColor",Vec4(1.0,1.0,1.0, 1.0))
        self.skydome.setBin('background', 1)
        self.skydome.setTwoSided(True)
        self.skydome.node().setBounds(OmniBoundingVolume())
        self.skydome.node().setFinal(1)
        self.skydome.setShader(Shader.load(Shader.SLGLSL, 'shaders/cloud_v.glsl', 'shaders/cloud_f.glsl'))
        self.skydome.hide(MASK_SHADOW)
        self.skydome.setTransparency(TransparencyAttrib.MNone, 1)
        
        #light
        self.light_manager=LightManager()
        #sun
        self.sun=self.light_manager.addLight(pos=(256.0, 256.0, 200.0), color=(0.9, 0.9, 0.9), radius=10000.0)
        render.setShaderInput('daytime', 12.0)

        #ambient light
        self.light_manager.ambientLight(0.15, 0.15, 0.2)    
        
        #render shadow map
        self.shadow_camera=None
        self.depth_buffer=None
        self.sun_node=render.attachNewNode('sun_node')
        self.sun_node.setPos(256, 256, 0)        
        self._makeShadowBuffer()
        
        self.setTime(7.0)
        
    def _makeShadowBuffer(self):
        hpr=(90, -90, 0)
        pos=(256, 256, 200)
        if self.shadow_camera:
            hpr=self.shadow_camera.getHpr(render)
            pos=self.shadow_camera.getPos(render)
            self.shadow_camera.removeNode() 
            self.sun_node.setPos(256, 256, 0)            
        if self.depth_buffer:
            self.depth_buffer.clearRenderTextures()    
            engine = base.win.getGsg().getEngine()
            engine.removeWindow(self.depth_buffer)    
        if cfg['simple-shaders']:    
            self.shadow_camera=render.attachNewNode('fake_shadow_camera_node')
            self.shadow_camera.setPos(pos)
            self.shadow_camera.setHpr(hpr)        
            self.shadow_camera.wrtReparentTo(self.sun_node)
            return
        #render shadow map
        depth_map = Texture()
        depth_map.setFormat( Texture.FDepthComponent)
        depth_map.setWrapU(Texture.WMBorderColor)
        depth_map.setWrapV(Texture.WMBorderColor)
        depth_map.setBorderColor(Vec4(1.0, 1.0, 1.0, 1.0))
        #depth_map.setMinfilter(Texture.FTShadow )
        #depth_map.setMagfilter(Texture.FTShadow )
        depth_map.setMinfilter(Texture.FTNearest   )
        depth_map.setMagfilter(Texture.FTNearest   )
        props = FrameBufferProperties()
        props.setRgbColor(0)
        props.setDepthBits(1)
        props.setAlphaBits(0)
        props.set_srgb_color(False)
        buff_size=cfg['shadow-size']        
        self.depth_buffer = base.win.makeTextureBuffer("Shadow Buffer",
                                              buff_size,
                                              buff_size,
                                              to_ram = False,
                                              tex = depth_map,
                                              fbp = props)
        self.depth_buffer.setClearColor(Vec4(1.0,1.0,1.0,1.0))
        self.depth_buffer.setSort(-101)
        self.shadow_camera = base.makeCamera(self.depth_buffer)
        lens = OrthographicLens()
        shadow_area=cfg['shadow-area']
        lens.setFilmSize(shadow_area, shadow_area)
        self.shadow_camera.node().setLens(lens)
        self.shadow_camera.node().getLens().setNearFar(10,400)
        self.shadow_camera.node().setCameraMask(MASK_SHADOW)
        self.shadow_camera.reparentTo(render)
        #self.shadow_camera.node().showFrustum()
        self.shadow_camera.setPos(pos)
        self.shadow_camera.setHpr(hpr)
        
        self.shadow_camera.wrtReparentTo(self.sun_node)
        render.setShaderInput('shadow', depth_map)
        render.setShaderInput("bias", 1.0)
        render.setShaderInput('shadowCamera',self.shadow_camera)   
               
    def _blendPixels(self, p1, p2, blend):
        c1=[p1[0]/255.0,p1[1]/255.0,p1[2]/255.0, p1[3]/255.0]
        c2=[p2[0]/255.0,p2[1]/255.0,p2[2]/255.0, p2[3]/255.0]
        return Vec4( c1[0]*blend+c2[0]*(1.0-blend), c1[1]*blend+c2[1]*(1.0-blend), c1[2]*blend+c2[2]*(1.0-blend), c1[3]*blend+c2[3]*(1.0-blend))

    def setTime(self, time):
        sunpos=min(0.5, max(-0.5,(time-12.0)/14.0))
        render.setShaderInput('sunpos', sunpos)
        x1=int(time)
        x2=x1-1
        if x2<0:
            x2=0
        blend=time%1.0

        p1=self.skyimg.getPixel(x1, 0)
        p2=self.skyimg.getPixel(x2, 0)
        sun_color=self._blendPixels(p1, p2, blend)
        #sun_color[0]=sun_color[0]*1.3
        #sun_color[1]=sun_color[1]*1.3
        #sun_color[2]=sun_color[2]*1.3
        p1=self.skyimg.getPixel(x1, 1)
        p2=self.skyimg.getPixel(x2, 1)
        sky_color=self._blendPixels(p1, p2, blend)

        p1=self.skyimg.getPixel(x1, 2)
        p2=self.skyimg.getPixel(x2, 2)
        cloud_color=self._blendPixels(p1, p2, blend)

        p1=self.skyimg.getPixel(x1, 3)
        p2=self.skyimg.getPixel(x2, 3)
        fog_color=self._blendPixels(p1, p2, blend)
        fog_color[3]=(abs(sunpos)*0.1+0.01)

        if time<6.0 or time>18.0:
            p=0.0
        else:
            p=sunpos*-180.0

        self.sun_node.setP(p)
        self.light_manager.setLight(id=self.sun, pos=self.shadow_camera.getPos(render), color=sun_color, radius=10000.0)
        render.setShaderInput("sunColor",sun_color)
        render.setShaderInput("skyColor",sky_color)
        render.setShaderInput("cloudColor",cloud_color)
        render.setShaderInput("fog", fog_color)
