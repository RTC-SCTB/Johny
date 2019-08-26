#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from rise.rtx.urtxsocket import TcpClient
import threading
from rise.devices.helmet import Helmet
from rise.utility.video import Video, VIDEO_IN_LAUNCH
import datetime

# словаро с описанием ошибок по номеру ошибки
errorDict = {
    0x03: "Не все калибровочные данные получены"
}


class Johny:
    """ Класс интерфейс Джонни """

    def __init__(self, host):
        self._client = None
        self.host = host
        self._video = Video()
        self.__exit = False
        self.errorList = []

    def __onReceive(self, data):
        """ Хендлер - заглушка """
        pass

    def __recvError(self, data):
        """ обработчик пришедших с робота ошибок """
        error = {"num": data[0],  # номер ошибки
                 "dlc": data[1],  # дополнение
                 "time": datetime.datetime.now(),  # время ошибки
                 "desc": errorDict.get(data[0])}  # описание

        self.errorList.append(error)

    def connect(self):
        self._client = TcpClient()
        self._client.subscribe(1, self.__recvError)
        self._client.subscribe("onReceive", self.__onReceive)
        self._client.connect(host=self.host)
        self._client.start()

    def disconnect(self):
        self._client.disconnect()
        del self._client
        self._client = None

    def setHeadPosition(self, angle0, angle1, angle2):
        self._client.sendPackage(2, (angle0, angle1, angle2))

    def calibrateHead(self):
        self._client.sendPackage(3, ())

    def videoState(self, state):
        if state:
            self._video.start(VIDEO_IN_LAUNCH)
        else:
            self._video.stop()
        self._client.sendPackage(4, (bool(state),))

    def move(self, scale):
        speed = scale  # TODO: scale to speed
        self._client.sendPackage(5, (int(speed),))

    def rotate(self, scale):
        speed = scale    # TODO: scale to speed
        self._client.sendPackage(6, (int(speed),))


if __name__ == "__main__":
    import random

    j = Johny(("localhost", 9096))
    j.connect()
    time.sleep(14)
    # j.calibrateHead()
    while True:
        # pos = (random.randint(-65, 65), random.randint(-50, 50), random.randint(-42, 42))
        # j.setHeadPosition(*pos)
        time.sleep(3)
