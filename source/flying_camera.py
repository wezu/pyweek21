from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from panda3d.core import *


class FlyingCamera():
    def __init__(self, offset=(0, -5, 2), angle=-15):
        #camera
        self.cam_node=render.attachNewNode("cam_node")
        base.cam.reparentTo(self.cam_node)
        base.cam.setPos(offset)
        base.cam.setP(angle)
    
    def _zoom(self, t):        
        base.cam.setY(base.cam.getY()+t)
        base.cam.setP(base.cam.getP()+t*3.0)
        base.cam.setZ(render, base.cam.getZ(render)-t*0.5)
        
    def zoomIn(self):
        LerpFunc(self._zoom,fromData=0,toData=0.04, duration=1.0, blendType='easeOut').start()    
        
    def zoomOut(self):        
        LerpFunc(self._zoom,fromData=0,toData=-0.04, duration=1.0, blendType='easeOut').start()    
        
    def follow(self, target, dt, speed):
        self.cam_node.setPos(target.getPos(render))        
        orig_H = self.cam_node.getH(render)
        target_H = target.getH(render)
        # Make the rotation go the shortest way around.
        orig_H = fitSrcAngle2Dest(orig_H, target_H)

        # How far do we have to go from here?
        delta = abs(target_H - orig_H)
        if delta == 0:
            # We're already looking at the target.
            return
        # Figure out how far we should rotate in this frame, based on the
        # distance to go, and the speed we should move each frame.
        t = dt * delta *speed
        # If we reach the target, stop there.
        t = min(t, 1.0)
        new_H = orig_H + (target_H - orig_H) * t
        self.cam_node.setH(new_H)
