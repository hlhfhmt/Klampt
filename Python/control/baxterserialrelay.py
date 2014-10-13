#!/usr/bin/env python
"""Relays messages between ROS controller and Baxter controller in Klamp't
"""

import rosbaxtercontroller
from serialcontroller import ControllerClient
from klampt import *
import asyncore
import rospy

#read klampt_robot_file and optionally klampt_serial_port from parameter server
rospy.init_node('klampt_sim')
print rospy.get_param('/klampt_robot_file')
try:
    klampt_robot_model_fn = rospy.get_param('/klampt_robot_file')
except KeyError:
    print 'Error, ROS parameter "/klampt_model_name" doesn\'t exist.'
    print 'Set this using rosparam set klampt_model_name [KLAMPT .rob FILE]'
    exit(1)
try:
    klampt_serial_port = rospy.get_param('/klampt_serial_port')
    print "Using serial port",klampt_serial_port,"from parameter /klampt_serial_port"
except KeyError:
    klampt_serial_port = 3456
    print "Using serial port 3456 by default, use rosparam set"
    print "klampt_serial_port [PORT] if you want to change this."

#load robot file
world = WorldModel()
world.enableGeometryLoading(False)
res = world.readFile(klampt_robot_model_fn)
if not res: 
    print 'Error, could not load klampt model from',klampt_robot_model_fn
    exit(1)
if world.numRobots()==0:
    print 'Error, klampt model',klampt_robot_model_fn,'did not contain a robot'
    exit(1)
klampt_robot_model = world.robot(0)
print "Load successful"

#print some info
robotName = klampt_robot_model.getName()
linkNames = [klampt_robot_model.getLink(i).getName() for i in range(klampt_robot_model.numLinks())]
print "Running controller listening on topic /%s/limb/right/joint_command and"%(robotName,)
print "and /%s/limb/left/joint_command andd publishing on topic"%(robotName,)
print "/%s/joint_states"%(robotName,)
print "Klamp't link names are:",linkNames

#create the ROS controller
c = rosbaxtercontroller.make(klampt_robot_model)

#launch the serial client to connect to a given host and relay messages from the socket to/from ROS
host = 'localhost'
port = klampt_serial_port
s = ControllerClient((host,port),c)

try:
    asyncore.loop()
except KeyboardInterrupt:
    print "Ctrl+C pressed, exiting..."
