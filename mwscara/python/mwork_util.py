#!/usr/bin/env python3

from stdglue import *
import math
import hal

throw_exceptions = 1


def getlenghArm():
    global lenghtArm
    for x in range(0, 5):
        lenghtArm[x] = hal.get_value("scarakins.D%d" % (x + 1))
    # MESSAGE("X%.4f Y %s Z%.4f C%.4f C%.4f C%.4f"%(lenghtArm[0] ,lenghtArm[1] ,lenghtArm[2] ,lenghtArm[3],lenghtArm[4],lenghtArm[5]))


def scarakinematicInver(pos):
    lenghtArm = [0, 0, 0, 0, 0, 0]
    anglepos = [0, 0, 0, 0]
    try:     
        for x in range(5):
            lenghtArm[x] = hal.get_value("scarakins.D%d" % (x + 1))
        x, y, z, c = pos['x'], pos['y'], pos['z'], pos['c']
        q0 = q1 = 0
        a3 = math.radians(c)
        xt = x - lenghtArm[5] * math.cos(a3)
        yt = y - lenghtArm[5] * math.sin(a3)
        rsq = xt * xt + yt * yt
        cc = (rsq - lenghtArm[1] * lenghtArm[1] - lenghtArm[3] * lenghtArm[3]) / (2 * lenghtArm[1] * lenghtArm[3])
        if cc < -1:
            cc = -1
        elif cc > 1:
            cc = 1
        q1 = math.acos(cc)
        joint1 = float(hal.get_value("joint.1.motor-pos-cmd"))
        if joint1 < 0:
            q1 = -q1
        q0 = math.atan2(yt, xt)
        xt = lenghtArm[1] + lenghtArm[3] * math.cos(q1)
        yt = lenghtArm[3] * math.sin(q1)
        q0 = q0 - math.atan2(yt, xt)
        q0 = math.degrees(q0)
        q1 = math.degrees(q1)
        if q0 > 180:
            q0 = q0 - 360
        elif q0 < -180:
            q0 = 360 + q0
        anglepos = [q0, q1, z, c - (q0 + q1)]
        """
        if (anglepos[3] > 180):
            anglepos[3] =  anglepos[3] - 360
        elif (anglepos[3] < -180):
            anglepos[3] =   360 - anglepos[3]
        """
    except Exception as e:
        print(" - %s" % (e.error_message))
    return anglepos
