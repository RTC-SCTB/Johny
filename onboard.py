#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import can
import time
from rise.cannet.bot import Robot
from rise.board.robothandle import JohnyHandle

bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
robot = Robot(bus)
robot.online = True
robot.start()
jh = JohnyHandle(("localhost", 9099), robot)
jh.connect()
while True:
    time.sleep(3)
