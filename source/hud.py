from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toolkit import *

class HUD():
    def __init__(self):  
        
        self.top_left=pixel2d.attachNewNode('TopLeft')
        self.top_right=pixel2d.attachNewNode('TopRight')
        self.bottom_right=pixel2d.attachNewNode('BottomRight')
        self.bottom_left=pixel2d.attachNewNode('BottomLeft')
        self.top=pixel2d.attachNewNode('Top')
        self.bottom=pixel2d.attachNewNode('Bottom')
        self.left=pixel2d.attachNewNode('Left')
        self.right=pixel2d.attachNewNode('Right')
        self.center=pixel2d.attachNewNode('Center')
              
        self.fuel_gage=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/fuel.png', cfg['srgb']), 
                                    parent=self.top_left)  
        resetPivot2d(self.fuel_gage) 
        self.fuel_gage.setPos(pos2d(0,0))
        
        self.fuel_arrow=self.top_left.attachNewNode('fuel_arrow')
        self.fuel_arrow.setPos(pos2d(64,85))
        
        self.fuel_arrow_vis=DirectFrame(frameSize=rec2d(64,64),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/arrow.png', cfg['srgb']), 
                                    parent=self.top_left)  
        resetPivot2d(self.fuel_arrow_vis) 
        self.fuel_arrow_vis.setPos(pos2d(35,35))
        self.fuel_arrow_vis.wrtReparentTo(self.fuel_arrow)  
        
        
        self.speed_gage=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/mph.png', cfg['srgb']), 
                                    parent=self.top_right)  
        resetPivot2d(self.speed_gage) 
        self.speed_gage.setPos(pos2d(-128,0))
        
        self.speed_arrow=self.top_right.attachNewNode('speed_arrow')
        self.speed_arrow.setPos(pos2d(65-128,64))
        
        self.speed_arrow_vis=DirectFrame(frameSize=rec2d(64,64),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/arrow.png', cfg['srgb']), 
                                    parent=self.top_right)  
        resetPivot2d(self.speed_arrow_vis) 
        self.speed_arrow_vis.setPos(pos2d(35-128,13))
        self.speed_arrow_vis.wrtReparentTo(self.speed_arrow)  
        #self.speed_arrow.setR(54)
        
        self.grradar_frame=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/radar_frame.png', cfg['srgb']), 
                                    parent=self.bottom_left)  
        resetPivot2d(self.grradar_frame) 
        self.grradar_frame.setPos(pos2d(0,-128))
        
        self.grradar_display=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/radar_frame.png', cfg['srgb']), 
                                    parent=self.bottom_left)  
        resetPivot2d(self.grradar_display) 
        self.grradar_display.setPos(pos2d(0,-128))
        
        
        self.gradar_axis=self.bottom_left.attachNewNode('gradar_axis')
        self.gradar_axis.setPos(pos2d(64,64-128))
        
        self.gradar_ping=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/radar.png', cfg['srgb']), 
                                    parent=self.bottom_left)  
        resetPivot2d(self.gradar_ping) 
        self.gradar_ping.setPos(pos2d(0,-128))
        self.gradar_ping.wrtReparentTo(self.gradar_axis) 
        
        LerpHprInterval(self.gradar_axis, 5.0, (0,0, 360), (0,0,0)).loop()
        
        self.font = loader.loadFont(path+'gui/font.ttf')
        self.font.setPixelsPerUnit(45)        
        
        self.counter=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,0),
                                    text="100%",
                                    text_font=self.font,                                
                                    text_scale = 45,
                                    text_fg=(0.0282, 0.54,0.0165, 1.0),   
                                    textMayChange=1,
                                    text_pos=(-60,10),
                                    parent=self.bottom_left)  
        resetPivot2d(self.counter) 
        self.counter.setPos(pos2d(0,-256))
        
        
        self.help_frame=DirectFrame(frameSize=rec2d(512,512),
                                    frameColor=(1,1,1,1),
                                    frameTexture=tex(path+'gui/help.png', cfg['srgb']), 
                                    parent=self.center)  
        resetPivot2d(self.help_frame) 
        self.help_frame.setPos(pos2d(-256,-256))
        
        self.updateGuiNodes()        
        self.showFuel(100)
        self.showSpeed(0)
    
    def hide(self):
        self.top_left.hide()
        self.top_right.hide()
        self.bottom_right.hide()
        self.bottom_left.hide()
        self.top.hide()
        self.bottom.hide()
        self.left.hide()
        self.right.hide()
        #self.center.hide()
    
    def show(self):
        self.top_left.show()
        self.top_right.show()
        self.bottom_right.show()
        self.bottom_left.show()
        self.top.show()
        self.bottom.show()
        self.left.show()
        self.right.show()
        #self.center.show()
        
    def showSpeed(self, kmph):
        if kmph<0.0:
            kmph=0.0
        #0=~ -135 deg, 100=~54
        angel=(kmph*1.89)-135
        self.speed_arrow.setR(angel)
        
    def showFuel(self, percent):
        #F =45 deg, E= -45deg.
        angel=(percent*0.9)-45    
        self.fuel_arrow.setR(angel)
        
    def updateGuiNodes(self):        
        wp=base.win.getProperties()
        winX = wp.getXSize()
        winY = wp.getYSize()    
        #print winX, winY    
        self.top_left.setPos(pos2d(0,0))
        self.top_right.setPos(pos2d(winX,0))        
        self.bottom_right.setPos(pos2d(winX,winY))
        self.bottom_left.setPos(pos2d(0,winY))
        self.top.setPos(pos2d(winX/2,0))
        self.bottom.setPos(pos2d(winX/2,winY))
        self.left.setPos(pos2d(0,winY/2))
        self.right.setPos(pos2d(winX,winY/2))
        self.center.setPos(pos2d(winX/2,winY/2))
