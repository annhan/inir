#!/usr/bin/env python3


import time
import hal
from interpreter import *
from stdglue import *
from mwork_util import scarakinematicInver


throw_exceptions = 1

xold = 0
xyol = 0
throw_exceptions = 1
offsetPosi = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
AxisJoint = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
TestPARA = 0
CoordinateNumber = 0
CoordinateGcode = ["G54", "G55", "G56", "G57", "G58", "G59", "G59.1", "G59.2", "G59.3"]
lenghtArm = [0, 0, 0, 0, 0, 0]

def m432remap(self):
    global TestPARA
    # hal.component_exists("TestPARA")
    debug = hal.get_value("joint.0.free-pos-cmd")
    return INTERP_OK


def m435remap(self):
    global lenghtArm
    for x in range(5):
        lenghtArm[x] = hal.get_value("scarakins.D%d" % (x + 1))
    # print("lenghtArm %d-%d-%d-%d-%d-%d" %(lenghtArm[0],lenghtArm[1],lenghtArm[2],lenghtArm[3],lenghtArm[4],lenghtArm[5]))
    return INTERP_OK


def m462OutAnDelay(self, **words):
    """ remap function which does the equivalent of M62, but via Python """
    p = int(words['p'])  # pin OUT
    q = float(words['q'])  # delay time
    try:
        self.execute(f"M64 P{p}")
        self.execute(f"M180 P{q}")
        self.execute(f"M65 P{p}")
    except InterpreterException as e:
        self.set_errormsg(e)
        print("m462OutAnDelay %d: '%s' - %s" % (e.line_number,e.line_text, e.error_message))
        yield  INTERP_ERROR
    yield INTERP_EXECUTE_FINISH
    return INTERP_OK


def m463OutRCAnDelay(self, **words):
    p = float(words['p'])  # goc
    q = float(words['q'])  # delay time
    hal.set_p("hm2_7i80.0.rcpwmgen.00.width", str(p))
    self.execute(f"M180 P{q}")
    yield INTERP_EXECUTE_FINISH
    return INTERP_OK


# def convertJoinMode(self):
#     try:
#         value = hal.get_value("motion.switchkins-type")
#         if value != 1:
#             SWITCHKINS_PIN = 3
#             kinstype = 1
#             #CoordinateNumber = self.params[5220]
#             self.execute("M66 E0 L0")
#             self.execute("M129")
#             self.execute("M68 E%d Q%d" % (SWITCHKINS_PIN, kinstype))
#             self.execute("M66 E0 L0")
#         return True
#     except InterpreterException as e:
#         print("convertJoinMode %d: '%s' - %s" % (e.line_number,e.line_text, e.error_message))
#         return False
#     except:
#         return False

# def convertWorldMode(self):
#     try:
#         value = hal.get_value("motion.switchkins-type")
#         if value != 0:
#             SWITCHKINS_PIN = 3
#             kinstype = 0
#             self.execute("M66 E0 L0")
#             self.execute("M128")
#             self.execute("M68 E%d Q%d" % (SWITCHKINS_PIN, kinstype))
#             self.execute("M66 E0 L0")
#         return True
#     except InterpreterException as e:
#         print("convertWorldMode %d: '%s' - %s" % (e.line_number,e.line_text, e.error_message))
#         return False
#     except:
#         return False
def m441open(self, **words):  # convert to world mode
    # Chu y muon thay doi switchkins thi can thuc hien het lenh trong bo dem
    # nên cần tạo 1 gcode để thực hiện việc chờ hết bộ đệm trước khi thực hiện lệnh switchkind
    value = hal.get_value("motion.switchkins-type")
    if value != 0:
        SWITCHKINS_PIN = 3
        kinstype = 0     
        #self.execute("M66 E0 L0")
        self.execute("M128")
        self.execute("M68 E%d Q%d" % (SWITCHKINS_PIN, kinstype))
        self.execute("M66 E0 L0")
    #yield INTERP_OK
    return INTERP_OK
def m440close(self, **words):  # convert to world mode
    # Chu y muon thay doi switchkins thi can thuc hien het lenh trong bo dem
    # nên cần tạo 1 gcode để thực hiện việc chờ hết bộ đệm trước khi thực hiện lệnh switchkind
    value = hal.get_value("motion.switchkins-type")
    if value != 0:
        SWITCHKINS_PIN = 3
        kinstype = 0     
        #self.execute("M66 E0 L0")
        self.execute("M128")
        self.execute("M68 E%d Q%d" % (SWITCHKINS_PIN, kinstype))
        self.execute("M66 E0 L0")
    #yield INTERP_OK
    return INTERP_OK
def m438remap(self, **words):  # convert to world mode
    # Chu y muon thay doi switchkins thi can thuc hien het lenh trong bo dem
    # nên cần tạo 1 gcode để thực hiện việc chờ hết bộ đệm trước khi thực hiện lệnh switchkind
    value = hal.get_value("motion.switchkins-type")
    if value != 0:
        SWITCHKINS_PIN = 3
        kinstype = 0     
        #self.execute("M66 E0 L0")
        self.execute("M128")
        self.execute("M68 E%d Q%d" % (SWITCHKINS_PIN, kinstype))
        self.execute("M66 E0 L0")
    #yield INTERP_OK
    return INTERP_OK

def m439remap(self, **words):  # convert to joint mode
    value = hal.get_value("motion.switchkins-type")
    if value != 1:
        SWITCHKINS_PIN = 3
        kinstype = 1
        #self.execute("M66 E0 L0")
        self.execute("M129")
        self.execute("M68 E%d Q%d" % (SWITCHKINS_PIN, kinstype))
        self.execute("M66 E0 L0")
    #yield INTERP_OK  
    return INTERP_OK


def check_coords(self, axis, wanted):
    actual = getattr(self, f"current_{axis}")
    wanted = float(wanted)
    if abs(actual - wanted) > 0.000001:
        self.execute("(ERROR  %s:  %0.1f != %0.1f)" % (axis, actual, wanted))
    else:
        self.execute("(%s: %0.1f = %0.1f)" % (axis, actual, wanted))

#---------------------------------------------------------------------------------------
# ReturnERROR()
#---------------------------------------------------------------------------------------
def ReturnERROR():
    print("Before return INTERP_ERROR")
    yield  INTERP_ERROR

#
# Move Joint in world mode
# Toa do nhap vao la toa do worldmode
# ex: Move to X50 Y50 in world mode
# my code will caculater invert kinematic to get joint pos
# After conver mode to joint mode, move and return world mode
## https://github.com/LinuxCNC/linuxcnc/blob/master/src/emc/nml_intf/canon.hh#L245
# Khong ne dung execute ma dung Thay vì self.execute("G53 G0..."), hãy thử sử dụng emccanon.STRAIGHT_TRAVERSE()
def g01_move_joint_by_world(self, **words):
    pos = {'x': 0, 'y': 0, 'z': 0, 'c': 0}

    # Get POS    
    feed_rate = ""
    type_Gcode = "G0"
    have_yield = False
    if 'f' in words:
        type_Gcode = "G1"
        feed_rate = f"f{words['f']}"      
    cmd = {'x', 'y', 'z', 'c'}
    for name in cmd:
        if name in words:
            pos[name] = float(words[name])
        else:
            prev_mode = hal.get_value("motion.switchkins-type")
            if prev_mode !=0: # CHUYEN QUA TOA DO WORK DE LAY VI TRI
                yield INTERP_EXECUTE_FINISH 
                self.execute("M438")
                yield INTERP_EXECUTE_FINISH   
                have_yield = True
            pos[name] = float(hal.get_value(f'axis.{name}.pos-cmd'))
            
    # Chuyen QUA JOINT MODE  
     
    prev_mode = hal.get_value("motion.switchkins-type")
    if prev_mode != 1:
        yield INTERP_EXECUTE_FINISH 
        self.execute("M439")
        yield INTERP_EXECUTE_FINISH     
        have_yield = True
    #Tinh TOAN KINEMATIC 
          
    anglepos = scarakinematicInver(pos)
    gcodecmd = "G53 {} x{:.2f} y{:.2f} z{:.2f} c{:.2f} {}".format(type_Gcode, anglepos[0], anglepos[1], anglepos[2], anglepos[3], feed_rate)
    # THuc hien gcode
    try:    
        self.execute(gcodecmd)
        #yield INTERP_EXECUTE_FINISH 
        print("g0.1 {} {}".format(time.time(),gcodecmd))
        yield INTERP_OK

    except Exception as e:
        print("G01 ERROR {}".format(e))
        yield INTERP_ERROR


def g04_move_world(self, **words): 
    """ # Move  in world mode
        # ex: Move to X50 Y50 in world mode
        # After conver mode to world mode, move and return world mode

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """

    pos = {'x': "", 'y': "", 'z': "", 'c': "",'f': ""}
    have_yield = False
    prev_mode = hal.get_value("motion.switchkins-type")
    if prev_mode != 0:
        have_yield = True
        yield INTERP_EXECUTE_FINISH 
        self.execute("M438")
        yield INTERP_EXECUTE_FINISH 
        
    cmd = ['x','y','z','c','f']
    typeGcode = "G0"
    if 'f' in words:
        typeGcode = "G1"
    #for name in cmd:   
    for name in words:
        pos[name] = " {}{:.2f}".format(name, float(words[name]))
    gcodecmd = "G53 {}{}{}{}{}{} ".format(typeGcode, pos['x'], pos['y'], pos['z'], pos['c'], pos['f'])
    try:
        self.execute(gcodecmd)
        print("G0.4 {} {}".format(time.time(),gcodecmd))
        yield INTERP_OK
    except:
        yield INTERP_ERROR


def g01_move_joint_by_world_emccannon(self, **words):
    pos = {'x': 0, 'y': 0, 'z': 0, 'c': 0}

    # Get POS    
    feed_rate = ""
    type_Gcode = "G0"
    have_yield = False
    if 'f' in words:
        type_Gcode = "G1"
        feed_rate = f"f{words['f']}"      
    cmd = {'x', 'y', 'z', 'c'}
    for name in cmd:
        if name in words:
            pos[name] = float(words[name])
        else:
            prev_mode = hal.get_value("motion.switchkins-type")
            if prev_mode !=0: # CHUYEN QUA TOA DO WORK DE LAY VI TRI
                yield INTERP_EXECUTE_FINISH 
                self.execute("M438")
                yield INTERP_EXECUTE_FINISH   
                have_yield = True
            pos[name] = float(hal.get_value(f'axis.{name}.pos-cmd'))
            
    # Chuyen QUA JOINT MODE  
     
    prev_mode = hal.get_value("motion.switchkins-type")
    if prev_mode != 1:
        yield INTERP_EXECUTE_FINISH 
        self.execute("M439")
        yield INTERP_EXECUTE_FINISH     
        have_yield = True
    #Tinh TOAN KINEMATIC 
          
    anglepos = scarakinematicInver(pos)
    gcodecmd = "G53 {} x{:.2f} y{:.2f} z{:.2f} c{:.2f} {}".format(type_Gcode, anglepos[0], anglepos[1], anglepos[2], anglepos[3], feed_rate)
    # THuc hien gcode
    try: 
        self.x_init = round(emccanon.GET_EXTERNAL_POSITION_X(), 3)
        self.y_init = round(emccanon.GET_EXTERNAL_POSITION_Y(), 3)
        self.z_init = round(emccanon.GET_EXTERNAL_POSITION_Z(), 3)
        self.a_init = round(emccanon.GET_EXTERNAL_POSITION_A(), 3)
        if type_Gcode == 'G0':
            emccanon.STRAIGHT_TRAVERSE(2, anglepos[0], anglepos[1], anglepos[2], self.a_init, 0, anglepos[3], 0, 0, 0)
        else:
            emccanon.SET_FEED_MODE(0, 0)
            emccanon.SET_FEED_RATE(float(feed_rate))
            emccanon.STRAIGHT_FEED(2, anglepos[0], anglepos[1], anglepos[2], self.a_init, 0, anglepos[3], 0, 0, 0)        
        #yield INTERP_EXECUTE_FINISH 
        print("g0.1 {} {}".format(time.time(),gcodecmd))
        yield INTERP_OK
        
    except Exception as e:
        print("G01 ERROR {}".format(e))
        yield  INTERP_ERROR
    return INTERP_OK

def g04_move_world_emccannon(self, **words): 
    """ # Move  in world mode
        # ex: Move to X50 Y50 in world mode
        # After conver mode to world mode, move and return world mode

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """

    pos = {'x': "", 'y': "", 'z': "", 'c': "",'f': ""}

    prev_mode = hal.get_value("motion.switchkins-type")
    if prev_mode != 0:
        yield INTERP_EXECUTE_FINISH 
        self.execute("M438")
        yield INTERP_EXECUTE_FINISH 
    
    cmd = ['x','y','z','c','f']
    typeGcode = "G0"
    if 'f' in words:
        typeGcode = "G1"
    #for name in cmd:   
    for name in words:
        pos[name] = " {}{:.2f}".format(name, float(words[name]))
    gcodecmd = "G53 {}{}{}{}{}{} ".format(typeGcode, pos['x'], pos['y'], pos['z'], pos['c'], pos['f'])
    try:
        self.a_init = round(emccanon.GET_EXTERNAL_POSITION_A(), 3)
        feed_rate = round(float(pos['f']),2)
        if typeGcode == 'G0':
            emccanon.STRAIGHT_TRAVERSE(2, pos['x'], pos['y'], pos['z'], self.a_init, 0, pos['c'], 0, 0, 0)
        else:
            emccanon.SET_FEED_MODE(0, 0)
            emccanon.SET_FEED_RATE(feed_rate)
            emccanon.STRAIGHT_FEED(2, pos['x'], pos['y'], pos['z'], self.a_init, 0, pos['c'], 0, 0, 0)
        print("G0.4 {} {}".format(time.time(),gcodecmd))
        #yield INTERP_EXECUTE_FINISH 
        yield INTERP_OK
    except:
        return INTERP_ERROR
    return INTERP_OK    
#
# Move Joint. If world mode, my code will convert to joint mode to move and back to world mode
# Toa do nhap vao la toa do joint mode
# Ex: G0.2 X20 Y30 
# 
# Or with F: G0.2 X20 Y30 F1000
#
def g02_move_joint(self, **words):
    pos = {'x': "", 'y': "", 'z': "", 'c': "", 'f':""}
    prev_mode = hal.get_value("motion.switchkins-type")
    if prev_mode != 1:
        yield INTERP_EXECUTE_FINISH 
        self.execute("M439")
        yield INTERP_EXECUTE_FINISH  
        
    typeGcode = "G0"  
    if 'f' in words:
        typeGcode = "G1"        
        
    for name in words:
        pos[name] = " {}{:.2f}".format(name, float(words[name]))  
        
    gcodecmd = "G53 {}{}{}{}{}{} ".format(typeGcode, pos['x'], pos['y'], pos['z'], pos['c'], pos['f'])    
    # THuc hien gcode
    try:    
        self.execute(gcodecmd)
        print("g0.2 {} {}".format(time.time(),gcodecmd))
        yield INTERP_OK
        # yield INTERP_EXECUTE_FINISH 
    except Exception as e:
        print("G2 ERROR {}".format(e))
        yield  INTERP_ERROR            
    return INTERP_OK         
       

def m464_move_step(self, **words):
    """ Di chuyen mâm xoay

    Returns:
        _type_: _description_

    Yields:
        _type_: _description_
    """

    p = float(words['p'])  # goc
    pos_cmd = float(hal.get_value("hm2_7i80.0.stepgen.05.position-cmd"))
    value = pos_cmd + p
    print(pos_cmd)
    hal.set_p("hm2_7i80.0.stepgen.05.position-cmd", str(value))
    yield INTERP_OK
    return INTERP_OK
