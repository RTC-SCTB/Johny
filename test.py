#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from rise.onpult.robot import Johny

j = Johny(("localhost", 9098))
j.connect()
time.sleep(14)
j.start()
# j.calibrateHead()
while True:
    # pos = (random.randint(-65, 65), random.randint(-50, 50), random.randint(-42, 42))
    # j.setHeadPosition(*pos)
    time.sleep(3)
