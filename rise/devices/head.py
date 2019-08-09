import random

import can
import time
from cannet import steppercontroller, bot
from cannet.steppercontroller import WorkMode, CalibrationMode


class Head:
    """ Класс поворотной головы Джонни """

    def __init__(self, stepController):
        self._stepController = stepController
        self._anglesRange = (
            (-65, 65), (-50, 50), (-42, 42))  # предельные значения углов, на которые может повернуться голова

    def start(self):
        """ Запускаем работу головы """
        # параметры для двигателя 0
        self._stepController.setParamRequest(0x02, 150)  # Calibrate step length
        self._stepController.setParamRequest(0x03, 30)  # Min step length
        self._stepController.setParamRequest(0x04, 50)  # Max step length
        self._stepController.setParamRequest(0x05, 1)  # Accel brake step

        # параметры для двигателя 1
        self._stepController.setParamRequest(0x0F, 100)  # Calibrate step length
        self._stepController.setParamRequest(0x10, 20)  # Min step length
        self._stepController.setParamRequest(0x11, 80)  # Max step length
        self._stepController.setParamRequest(0x12, 2)  # Accel brake step

        # параметры для двигателя 2
        self._stepController.setParamRequest(0x1C, 100)  # Calibrate step length
        self._stepController.setParamRequest(0x1D, 20)  # Min step length
        self._stepController.setParamRequest(0x1E, 80)  # Max step length
        self._stepController.setParamRequest(0x1F, 2)  # Accel brake step

        self._stepController.setWorkMode(0, WorkMode.CONTROL_POSITION)
        self._stepController.setWorkMode(1, WorkMode.CONTROL_POSITION)
        self._stepController.setWorkMode(2, WorkMode.CONTROL_POSITION)

        self.calibrate()  # запускаем калибровку

    def calibrate(self):
        """ Калибровка углов головы """
        self._stepController.calibrate(0, CalibrationMode.FULL)
        self._stepController.calibrate(1, CalibrationMode.FULL)
        self._stepController.calibrate(2, CalibrationMode.FULL)
        """ После калиюровки, новые значения диапазонов углов попадают в экземпляер контроллера """

    def setAllPosition(self, *angles):
        """ Устанавливает позицию моторов в положение по заданному углу в градусах"""
        position = [0, 0, 0]
        angles = [*angles]  # разворачиваем кортеж в список
        ar = self._anglesRange  # для сокращения кода
        pr = (self._stepController.getParamByNum(0x0D)[0],  # верхний предел допустимого поворота в попугаях(нижний
              self._stepController.getParamByNum(0x1A)[0],  # предел равен 0)
              self._stepController.getParamByNum(0x27)[0])

        checkRange = lambda x, limits: min(max(limits[0], x), limits[1])  # при привышении диапазона ставим крайние
        # значения

        for i in range(3):
            angles[i] = checkRange(angles[i], ar[i])
            length = ar[i][1] - ar[i][0]  # получаем длину допустимого диапазона в углах
            position[i] = int(((angles[i] + (length / 2)) / length) * pr[i])

        for i in range(3):
            self._stepController.setPosition(i, position[i])


if __name__ == "__main__":
    bus = can.interface.Bus(channel="can0", bustype='socketcan_native')
    robot = bot.Robot(bus)
    robot.online = True
    step = steppercontroller.StepperController(robot, 0x230)
    robot.addDevice(step)
    robot.start()
    head = Head(step)
    head.start()
    time.sleep(10)
    while True:
        pos = (random.randint(-65, 65), random.randint(-50, 50), random.randint(-42, 42))
        head.setAllPosition(*pos)
        time.sleep(3)
