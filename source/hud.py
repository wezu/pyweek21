from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toolkit import rec2d, pos2d, resetPivot2d

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
                                    frameTexture=path+'gui/fuel.png', 
                                    parent=self.top_left)  
        resetPivot2d(self.fuel_gage) 
        self.fuel_gage.setPos(pos2d(0,0))
        
        self.fuel_arrow=self.top_left.attachNewNode('fuel_arrow')
        self.fuel_arrow.setPos(pos2d(64,85))
        
        self.fuel_arrow_vis=DirectFrame(frameSize=rec2d(64,64),
                                    frameColor=(1,1,1,1),
                                    frameTexture=path+'gui/arrow.png', 
                                    parent=self.top_left)  
        resetPivot2d(self.fuel_arrow_vis) 
        self.fuel_arrow_vis.setPos(pos2d(35,35))
        self.fuel_arrow_vis.wrtReparentTo(self.fuel_arrow)  
        
        
        self.speed_gage=DirectFrame(frameSize=rec2d(128,128),
                                    frameColor=(1,1,1,1),
                                    frameTexture=path+'gui/mph.png', 
                                    parent=self.top_right)  
        resetPivot2d(self.speed_gage) 
        self.speed_gage.setPos(pos2d(-128,0))
        
        self.speed_arrow=self.top_right.attachNewNode('speed_arrow')
        self.speed_arrow.setPos(pos2d(65-128,64))
        
        self.speed_arrow_vis=DirectFrame(frameSize=rec2d(64,64),
                                    frameColor=(1,1,1,1),
                                    frameTexture=path+'gui/arrow.png', 
                                    parent=self.top_right)  
        resetPivot2d(self.speed_arrow_vis) 
        self.speed_arrow_vis.setPos(pos2d(35-128,13))
        self.speed_arrow_vis.wrtReparentTo(self.speed_arrow)  
        #self.speed_arrow.setR(54)
        
        
        
        
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
        self.center.hide()
    
    def show(self):
        self.top_left.show()
        self.top_right.show()
        self.bottom_right.show()
        self.bottom_left.show()
        self.top.show()
        self.bottom.show()
        self.left.show()
        self.right.show()
        self.center.show()
        
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
