from panda3d.core import *
from panda3d.bullet import *

class Terrain():
    def __init__(self, world, worldNP):
        self.world=world
        self.worldNP=worldNP
        self.collision=None        
        self.maps={'height':None, 'atr1':None, 'atr2':None}
        self.textures={1:None, 2:None, 3:None, 4:None, 5:None, 6:None}
        
        self.tex_diffuse_path=path+'terrain_tex/diffuse/'
        self.tex_normal_path=path+'terrain_tex/normal/'
        self.tex_ext=".dds"
        self.mesh=None
        render.setShaderInput("z_scale", 100.0)
        
    def loadMesh(self, mesh_file):
        self.mesh=loader.loadModel(mesh_file)
        self.mesh.reparentTo(render)
        self.loadCollisionMesh(self.mesh)
        
    def loadCollisionMesh(self, mesh):          
        bullet_mesh = BulletTriangleMesh()
        geomNodes = mesh.findAllMatches('**/+GeomNode')
        geomNode = geomNodes.getPath(0).node()
        geom = geomNode.getGeom(0)
        bullet_mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(bullet_mesh, dynamic=False, bvh=True ) 
        if self.collision:
            self.world.remove(self.collision.node())
            self.collision.removeNode()
        self.collision = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
        self.collision.node().addShape(shape)
        self.collision.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(self.collision.node())
        #self._showIfReady()
        
    def setTextures(self, tex_id_list):
        for i, tex_id in enumerate(tex_id_list,1):
            self.setTexturesByID(tex_id, i)
        
    def setTexturesByID(self, texture_id, stage_id):
        self.textures[stage_id]=texture_id
        diffuse_tex=self.tex_diffuse_path+str(texture_id)+self.tex_ext
        normal_tex=self.tex_normal_path+str(texture_id)+self.tex_ext
        diffuse_stage='tex{0}'.format(stage_id)
        normal_stage='tex{0}n'.format(stage_id)
        self.setTex(diffuse_tex, diffuse_stage)
        self.setTex(normal_tex, normal_stage, is_normal_map=True)
        
    def setTex(self, texture, stage, is_normal_map=False, anisotropicDegree=2):
        new_tex=loader.loadTexture(texture, anisotropicDegree=anisotropicDegree)        
        if cfg["srgb"] and not is_normal_map:
            tex_format=new_tex.getFormat()  
            if tex_format==Texture.F_rgb:
                tex_format=Texture.F_srgb
            elif tex_format==Texture.F_rgba or Texture.F_rgbm:
                tex_format=Texture.F_srgb_alpha   
            new_tex.setFormat(tex_format)  
            print "tex_format=",tex_format
        print "stage=", stage    
        print "texture=", texture
        #print "new_tex=", new_tex        
        #print "findTextureStage=", self.mesh.findTextureStage(stage)
        #print self.mesh.findAllTextureStages()
        new_tex.setMinfilter(Texture.FTLinearMipmapLinear)
        new_tex.setMagfilter(Texture.FTLinear)
        #self.mesh.setTexture(self.mesh.findTextureStage(stage), new_tex, 1)
        self.mesh.setShaderInput(stage, new_tex)
        
    def setMaps(self, folder=None, height=None, atr1=None, atr2=None):
        if folder:
            height=folder+'heightmap.png'
            atr1=folder+'detail0.png'
            atr2=folder+'detail1.png'
        self.maps={'height':height, 'atr1':atr1, 'atr2':atr2}
        render.setShaderInput("height",loader.loadTexture(height))
        self.mesh.setShaderInput("atr1",loader.loadTexture(atr1))
        self.mesh.setShaderInput("atr2",loader.loadTexture(atr2))        
        self.mesh.setShader(Shader.load(Shader.SLGLSL, path+"shaders/terrain_v.glsl",path+"shaders/terrain2_f.glsl"))        
        self.mesh.setShaderInput("tex_scale", 164.0)
        self.mesh.setTransparency(TransparencyAttrib.MNone, 1)
        self.mesh.node().setBounds(OmniBoundingVolume())
        self.mesh.node().setFinal(1)
        #self.mesh.setBin("background", 11)
