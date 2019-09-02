from rise.devices.head import Head
from rise.cannet.steppercontroller import StepperController
from rise.utility.video import Video, VIDEO_OUT_LAUNCH


class JohnyHandle:
    """ Класс, обрабатывающий сообщения и управляющий роботом на самом роботе """

    def __init__(self, robotHandle):
        self._robot = robotHandle
        self._step = StepperController(self._robot, 0x230)
        self._robot.addDevice(self._step)
        self._head = Head(self._step)
        self._video = Video()

    def start(self):
        self._head.start()

    def setHeadPosition(self, angle0, angle1, angle2):
        """ Установка позиции головы робота """
        self._head.setAllPosition(angle0, angle1, angle2)

    def setVideoState(self, dev, host, state):
        """ включение/выключение видео """
        if state:
            self._video.start(VIDEO_OUT_LAUNCH.format(device=dev, ip=host[0]))
        else:
            self._video.stop()

    def calibrateHead(self):
        """ калибровка головы робота """
        self._head.calibrate()

    def move(self, speed):
        """ движение вперед/назад """
        pass    # TODO: !!!

    def rotate(self, speed):
        """ поворот на месте """
        pass

