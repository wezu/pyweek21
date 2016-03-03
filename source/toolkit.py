from panda3d.core import *

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
