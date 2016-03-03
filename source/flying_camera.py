from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from panda3d.core import *


class FlyingCamera():
    def __init__(self, offset=(0, -5, 1.8), angle=-10):
        #camera
        self.cam_node=render.attachNewNode("cam_node")
        base.cam.reparentTo(self.cam_node)
        base.cam.setPos(offset)
        base.cam.setP(angle)
        
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
