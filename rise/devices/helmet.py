#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

import time
from openhmd import PyOpenHMD


class Helmet:
    """ Класс шлема VR """
    def __init__(self):
        self._hmd = PyOpenHMD()
        self._zeroAngles = [0, 0, 0]    # начальные углы

    def getRawAngles(self):
        # TODO: перенести это все в СИшный код
        self._hmd.poll()
        qx, qy, qz, qw = self._hmd.rotation[0:4]
        roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx ** 2 + qy ** 2)) * (180 / math.pi)
        pitch = math.asin(2 * (qw * qy - qz * qx)) * (180 / math.pi)
        yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy ** 2 + qz ** 2)) * (180 / math.pi)
        return yaw, pitch, roll

    def getAngles(self):
        za = self._zeroAngles
        yaw, pitch, roll = self.getRawAngles()
        return yaw - za[0], pitch - za[1], roll - za[2]

    def setZeroNow(self):
        """ установка начального значения по текущим значениям с очков """
        self._zeroAngles = self.getRawAngles()


if __name__ == "__main__":
    hmd = PyOpenHMD()
    while True:
        hmd.poll()
        time.sleep(0.2)
