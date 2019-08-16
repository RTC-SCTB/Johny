#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from rise.pult.robot import Johny

j = Johny(("localhost", 9099))
j.connect()
time.sleep(14)
j.start()
while True:
    time.sleep(3)
