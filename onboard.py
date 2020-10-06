#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading

import can
import time
from rise.cannet.bot import Robot
from rise.board.robothandle import JohnyHandle
from rise.rtx.urtxsocket import TcpServer
from can.interfaces import seeedstudio
import json

configuration = {}
with open("rise/board/robotconf.json", "r") as file:
    configuration = json.load(file)     # читаем конфигурационный файл и записываем данные в словарь

# bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
bus = seeedstudio.SeeedBus(channel=configuration["candevice"])  # Оболочка для переходника uart <-> can, который используется вместо аппаратного can  
time.sleep(1)
robot = Robot(bus)  # создаем менеджера для работы с can шиной 
robot.online = True     # разрешаем посылку онлайн меток в can
server = TcpServer()    # создаем сервер для пересылки пакетов
server.open(("", configuration["port"]))    # открываем его согласно файлу конфигурации
jh = None   # предварительно обЪявляем переменную хрянящую ссылку на экземпляр класса JohnyHandle


def sendError(num, dlc=0):
    """ сообщить об ошибке на пульт """
    server.sendPackage(1, (num, dlc))

 
""" далее идут обработчики приходящих пакетов, в зависимости от дескриптора пакета вызывается свой обработчик пакета """

def recvError(data):
    """ Обработчик пришедшей ошибки с пульта """
    pass


def recvCalibrate(data):
    """ обработчик события о пришествии комманды калибровки """
    try:
        jh.calibrateHead()
    except:
        pass


def recvPosition(data):
    """ обработчик события о пришествии позиции робота """
    try:
        jh.setHeadPosition(*data)
    except KeyError:
        sendError(0x03)  # отправляем код ошибки
    except:
        pass


def recvVideoState(data):
    """ Обработчик события о пришествии пакета включения/выключения (перезагрузки) видеопотока """
    try:
        jh.setVideoState(configuration["videodevice"], server.clientAddr, bool(data[0]))
    except:
        pass


def recvMove(data):
    """ Обработчик события о пришествии пакета движения робота """
    try:
        jh.move(data[0])
    except:
        pass


def recvRotate(data):
    """ Обработчик события о пришествии пакета поворота робота """
    try:
        jh.rotate(data[0])
    except:
        pass


def recvOnline(data):
    """ Обработчик события о пришествии онлайн метки по ip """
    global onlineCount
    onlineCount = 0


def onReceive(data):
    """ Хендлер - заглушка """
    pass


global onlineCount  # вспомогательная переменная для онлайн меток
onlineCount = 0


def th():
    """ ретранслятор онлайн меток из ip в can """
    global onlineCount
    while True:
        onlineCount += 1
        if onlineCount > 3:
            robot.online = False    # не шлем метки
        else:
            robot.online = True     # шлем метки
        time.sleep(1)


""" Подключаем обработчики событий к определенным событиям(дескрипторам) в пакетах """
server.subscribe(0, recvOnline)
server.subscribe(1, recvError)
server.subscribe(2, recvPosition)
server.subscribe(3, recvCalibrate)
server.subscribe(4, recvVideoState)
server.subscribe(5, recvMove)
server.subscribe(6, recvRotate)
server.subscribe("onReceive", onReceive)
server.start()
robot.start()
threading.Thread(daemon=True, target=th).start()

while True:
    server.connect(None)  # подключаемся в цикле, т.к. один раз запускаем скрипт на все время работы робота
    del jh  # т.к. цикл подключения/отключения производится в цикле, а данный скрипт запускается единожды, то решение с обновлением сервера решается удалением и созданием нового экземпляра JohnyHandle 
    jh = None
    jh = JohnyHandle(robot)
    jh.start()
