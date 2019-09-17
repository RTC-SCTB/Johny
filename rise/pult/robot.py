#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from rise.rtx.urtxsocket import TcpClient
from rise.pult.GstCV import CVGstreamer
# from rise.utility.video import Video, VIDEO_IN_LAUNCH
import datetime

# словаро с описанием ошибок по номеру ошибки
errorDict = {
    0x03: "Не все калибровочные данные получены"
}


class Johny:
    """ Класс интерфейс Джонни """

    def __init__(self, host):
        self._client = None
        self._host = host
        if host is not None:
            self.video = CVGstreamer(IP=host[0], RTP_RECV_PORT=5000, RTCP_RECV_PORT=5001, RTCP_SEND_PORT=5005,
                                      codec="JPEG", toAVS=False)
        else:
            self.video = CVGstreamer(IP=None, RTP_RECV_PORT=5000, RTCP_RECV_PORT=5001, RTCP_SEND_PORT=5005,
                                      codec="JPEG", toAVS=False)
        self.__exit = False
        self.errorList = []

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.video.IP = value[0]

    def __onReceive(self, data):
        """ Хендлер - заглушка """
        pass

    def __recvError(self, data):
        """ обработчик пришедших с робота ошибок """
        error = {"num": data[0],  # номер ошибки
                 "dlc": data[1],  # дополнение
                 "time": datetime.datetime.now(),  # время ошибки
                 "desc": errorDict.get(data[0])}  # описание

        for err in self.errorList:  # если такая ошибка уже есть
            if (error["num"] == err["num"]) and (error["dlc"] == err["dlc"]):
                return
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
            self.video.start()
        else:
            self.video.stop()
        self._client.sendPackage(4, (bool(state),))

    def move(self, scale):
        speed = scale  # TODO: scale to speed
        self._client.sendPackage(5, (int(speed),))

    def rotate(self, scale):
        speed = scale  # TODO: scale to speed
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
