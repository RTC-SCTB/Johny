#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import can
import time
from rise.cannet.bot import Robot
from rise.board.robothandle import JohnyHandle
from rise.rtx.urtxsocket import TcpServer
from can.interfaces import seeedstudio
import json

configuration = {}
with open("rise/board/robotconf.json", "r") as file:
    configuration = json.load(file)

#bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
bus = seeedstudio.SeeedBus(channel=configuration["candevice"])
time.sleep(1)
robot = Robot(bus)
robot.online = True
server = TcpServer()
server.open(("", configuration["port"]))
jh = JohnyHandle(robot)


def sendError(num, dlc=0):
    """ сообщить об ошибке на пульт """
    server.sendPackage(1, (num, dlc))


def recvError(data):
    """ Обработчик пришедшей ошибки с пульта """
    pass


def recvCalibrate(data):
    """ обработчик события о пришествии комманды калибровки """
    jh.calibrateHead()


def recvPosition(data):
    """ обработчик события о пришествии позиции робота """
    try:
        jh.setHeadPosition(*data)
    except KeyError:
        sendError(0x03)  # отправляем код ошибки


def recvVideoState(data):
    print(server.clientAddr)
    jh.setVideoState(configuration["videodevice"], server.clientAddr, bool(data[0]))


def recvMove(data):
    print("move", data[0])
    jh.move(data[0])


def recvRotate(data):
    print("rotate", data[0])
    jh.rotate(data[0])


def onReceive(data):
    """ Хендлер - заглушка """
    pass


server.subscribe(1, recvError)
server.subscribe(2, recvPosition)
server.subscribe(3, recvCalibrate)
server.subscribe(4, recvVideoState)
server.subscribe(5, recvMove)
server.subscribe(6, recvRotate)
server.subscribe("onReceive", onReceive)
server.start()
robot.start()
jh.start()

while True:
    server.connect(None)    # подключаемся в цикле, т.к. один раз запускаем скрипт на все время работы робота
