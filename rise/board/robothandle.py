import can
import time

from rise.rtx.urtxsocket import TcpServer
from rise.devices.head import Head
from rise.cannet.bot import Robot
from rise.cannet.steppercontroller import StepperController
from rise.utility.video import Video, VIDEO_OUT_LAUNCH


class JohnyHandle:
    """ Класс, обрабатывающий сообщения и управляющий роботом на самом роботе """

    def __init__(self, host, robotHandle):
        self._server = TcpServer()
        self._host = host
        self._robot = robotHandle
        self._step = StepperController(self._robot, 0x230)
        self._robot.addDevice(self._step)
        self._head = Head(self._step)
        self._server.subscribe(1, self.__recvError)
        self._server.subscribe(2, self.__recvPosition)
        self._server.subscribe(3, self.__recvCalibrate)
        self._server.subscribe(4, self.__recvVideoState)
        self._server.subscribe("onReceive", self.__onReceive)
        self._video = Video()

    def connect(self):
        self._server.connect(host=self._host)
        self._server.start()
        self._head.start()

    def setHeadPosition(self, angle0, angle1, angle2):
        self._head.setAllPosition(*pos)

    def sendError(self, num, dlc=0):
        """ сообщить об ошибке на пульт """
        self._server.sendPackage(1, (num, dlc))

    def __recvError(self, data):
        """ Обработчик пришедшей ошибки с пульта """
        pass

    def __recvCalibrate(self, data):
        """ обработчик события о пришествии комманды калибровки """
        self._head.calibrate()

    def __recvPosition(self, data):
        """ обработчик события о пришествии позиции робота """
        try:
            self._head.setAllPosition(*data)
        except KeyError:
            self.sendError(0x03)   # отправляем код ошибки

    def __recvVideoState(self, data):
        if data[0]:
            self._video.start(VIDEO_OUT_LAUNCH)
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
