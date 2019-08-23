#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket



"""
bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
robot = Robot(bus)
robot.online = True
robot.start()
jh = JohnyHandle(("", 9008), robot)
jh.connect()
jh._server._sock.settimeout(4.0)
while True:
    try:
        jh._server.connect(None)
    except socket.error as e:
        print(e)
    try:
        jh.sendError(0x03)
    except Exception as e:
        print(e)
"""

import can.interfaces.pcan.pcan
import can
import time
from rise.cannet.bot import Robot
from rise.board.robothandle import JohnyHandle
from rise.rtx.urtxsocket import TcpServer


bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
robot = Robot(bus)
robot.online = True
server = TcpServer()
server.open(("", 9009))
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
    jh.setVideoState(bool(data[0]))


def onReceive(data):
    """ Хендлер - заглушка """
    pass


server.subscribe(1, recvError)
server.subscribe(2, recvPosition)
server.subscribe(3, recvCalibrate)
server.subscribe(4, recvVideoState)
server.subscribe("onReceive", onReceive)
server.start()
robot.start()
jh.start()

while True:
    server.connect(None)    # подключаемся в цикле, т.к. один раз запускаем скрипт на все время работы робота

