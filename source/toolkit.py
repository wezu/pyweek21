from panda3d.core import *
from panda3d.bullet import *


def loadObject(model, H, pos, world, worldNP, root=render, collision_solid=None):
    
    new_model=loader.loadModel(model)
    new_model.clearModelNodes()
    new_model.reparentTo(root)
    new_model.setPos(render, pos)
    new_model.setH(render, H) 
    new_model.setShader(Shader.load(Shader.SLGLSL, path+'shaders/default_v.glsl', path+'shaders/default_f.glsl'))   
    if collision_solid:
        collision_mesh=loader.loadModel(collision_solid)
    else:
        collision_mesh=loader.loadModel(model)    
    collision_mesh.setPos(render, pos)
    collision_mesh.setH(render, H)    
    collision_mesh.flattenStrong()    
    bullet_mesh = BulletTriangleMesh()
    geomNodes = collision_mesh.findAllMatches('**/+GeomNode')
    geomNode = geomNodes.getPath(0).node()
    geom = geomNode.getGeom(0)
    bullet_mesh.addGeom(geom)
    shape = BulletTriangleMeshShape(bullet_mesh, dynamic=False, bvh=True ) 
    collision = worldNP.attachNewNode(BulletRigidBodyNode('object'))
    collision.node().addShape(shape)
    collision.setCollideMask(BitMask32.allOn())
    world.attachRigidBody(collision.node()) 
    return (new_model, collision)
    
def tex(file_name, srgb=False):
    texture=loader.loadTexture(file_name)
    tex_format=texture.getFormat()
    if srgb:
        if tex_format==Texture.F_rgb:
            tex_format=Texture.F_srgb
        elif tex_format==Texture.F_rgba:
            tex_format=Texture.F_srgb_alpha  
        texture.setFormat(tex_format) 
    return texture
         
def pos2d(x,y):
    return Point3(x,0,-y)
    
def rec2d(width, height):
    return (-width, 0, 0, height)
    
def resetPivot2d(frame):
    size=frame['frameSize']    
    frame.setPos(-size[0], 0, -size[3])        
    frame.flattenLight()
    frame.setTransparency(TransparencyAttrib.MAlpha)
    
def fixSrgbTextures(model):
    for tex_stage in model.findAllTextureStages():            
        tex=model.findTexture(tex_stage)
        if tex:
            file_name=tex.getFilename()
            tex_format=tex.getFormat()   
            #print tex_stage,  file_name, tex_format                
            newTex=loader.loadTexture(file_name)
            if tex_stage.getMode()==TextureStage.M_normal:
                tex_stage.setMode(TextureStage.M_normal_gloss)
            if tex_stage.getMode()!=TextureStage.M_normal_gloss:
                if tex_format==Texture.F_rgb:
                    tex_format=Texture.F_srgb
                elif tex_format==Texture.F_rgba:
                    tex_format=Texture.F_srgb_alpha    
            newTex.setFormat(tex_format)
            model.setTexture(tex_stage, newTex, 1)
