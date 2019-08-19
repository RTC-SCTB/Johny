#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import time
import math
from rise.rtx.urtx import proto
from rise.utility import eventmaster
from rise.rtx.urtxsocket import TcpClient
import threading
from rise.devices.helmet import Helmet
from rise.utility.video import VideoProcess


class Johny(threading.Thread):
    """ Класс интерфейс Джонни """

    def __init__(self, host):
        threading.Thread.__init__(self, daemon=True)
        self._client = TcpClient()
        self._helmet = Helmet()
        self._host = host
        self._video = VideoProcess()
        self.__exit = False

    def connect(self):
        self._client.connect(host=self._host)
        self._client.start()
        self.videoState(True)

    def setHeadPosition(self, angle0, angle1, angle2):
        self._client.sendPackage(2, (angle0, angle1, angle2))

    def calibrateHead(self):
        self._client.sendPackage(3, ())

    def exit(self):
        self.__exit = True

    def videoState(self, state):
        if state:
            self._video.start(["./rise/utility/videoin.sh"])
        else:
            self._video.stop()
        self._client.sendPackage(4, (bool(state), ))

    def run(self):
        self._helmet.setZeroNow()
        while not self.__exit:
            yaw, pitch, roll = self._helmet.getAngles()
            self.setHeadPosition(int(yaw), int(pitch), int(roll))
            time.sleep(0.1)


if __name__ == "__main__":
    import random
    j = Johny(("localhost", 9096))
    j.connect()
    time.sleep(14)
    #j.calibrateHead()
    while True:
        #pos = (random.randint(-65, 65), random.randint(-50, 50), random.randint(-42, 42))
        #j.setHeadPosition(*pos)
        time.sleep(3)

