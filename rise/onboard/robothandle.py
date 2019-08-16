import can
import time

from rise.rtx.urtxsocket import TcpServer
from rise.devices.head import Head
from rise.cannet.bot import Robot
from rise.cannet.steppercontroller import StepperController
from rise.utility.video import VideoProcess


class JohnyHandle:
    """ Класс, обрабатывающий сообщения и управляющий роботом на самом роботе """

    def __init__(self, host, robotHandle):
        self._server = TcpServer()
        self._host = host
        self._robot = robotHandle
        self._step = StepperController(self._robot, 0x230)
        self._robot.addDevice(self._step)
        self._head = Head(self._step)
        self._server.subscribe(2, self.__recvPosition)
        self._server.subscribe(3, self.__recvCalibrate)
        self._server.subscribe(4, self.__recvVideoState)
        self._server.subscribe("onReceive", self.__onReceive)
        self._video = VideoProcess()

    def connect(self):
        self._server.connect(host=self._host)
        self._server.start()
        self._head.start()

    def setHeadPosition(self, angle0, angle1, angle2):
        self._head.setAllPosition(*pos)

    def __recvCalibrate(self, data):
        """ обработчик события о пришествии комманды калибровки """
        self._head.calibrate()

    def __recvPosition(self, data):
        """ обработчик события о пришествии позиции робота """
        self._head.setAllPosition(*data)

    def __recvVideoState(self, data):
        print(data)
        if data[0]:
            self._video.start(["./videoout.sh"])
        else:
            self._video.stop()

    def __onReceive(self, data):
        """ Хендлер - заглушка """
        pass


if __name__ == "__main__":
    bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
    robot = Robot(bus)
    robot.online = True
    robot.start()
    jh = JohnyHandle(("localhost", 9099), robot)
    jh.connect()
    while True:

        time.sleep(3)
