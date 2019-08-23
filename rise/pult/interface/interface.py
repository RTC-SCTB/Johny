import json
import datetime
import gi
import  threading
import time
from rise.devices.helmet import Helmet
from rise.pult.robot import Johny

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class _SettingsWindow:
    def __init__(self, pult):
        self._owner = pult
        self._builder = Gtk.Builder()
        self._builder.add_from_file("rise/pult/interface/interface.glade")
        self._settingsWindow = self._builder.get_object("settingsWindow")
        self._calibrateButton = self._builder.get_object("calibrateButton")
        self._videoSwitch = self._builder.get_object("videoSwitch")
        self._settingsChooserButton = self._builder.get_object("settingsChooserButton")

        self._settingsChooserButton.connect("file-set", self.__confFilePathChange)
        self._calibrateButton.connect("clicked", self.__calibrateButtonClick)
        self._videoSwitch.connect("state-set", self.__videoSwitchClick)
        self._settingsWindow.connect("delete-event", self.__delete_event)

        self._calibrateButton.set_property("sensitive", self._owner.isConnected)
        self._videoSwitch.set_property("sensitive", self._owner.isConnected)
        self._settingsChooserButton.set_property("sensitive", not self._owner.isConnected)

        self._settingsWindow.show_all()

    def __calibrateButtonClick(self, w):
        self._owner.robot.calibrateHead()

    def __videoSwitchClick(self, w, state):
        self._owner.robot.videoState(state)

    def __confFilePathChange(self, w):
        try:
            self._owner.setConfigurationFromFile(w.get_uri()[6:])
        except:
            self._owner.printLog("Ошибка чтения файла конфигурации, проверьте его корректность")
        else:
            self._owner._onoffButton.set_property("sensitive", True)

    def __delete_event(self, widget, event, data=None):
        self._owner._settingsButton.set_property("sensitive", True)


class Pult:
    def __init__(self):
        """ развертываем интерфейс из glade """
        self._defaultConfigurationFilePath = "conf.json"
        self._configuration = None
        self._isConnected = False
        self.__exit = False
        self.robot = Johny(None)
        self._helmet = Helmet()

        self._builder = Gtk.Builder()
        self._builder.add_from_file("rise/pult/interface/interface.glade")

        self._mainWindow = self._builder.get_object("mainWindow")
        self._onoffButton = self._builder.get_object("onoffButton")
        self._settingsButton = self._builder.get_object("settingsButton")
        self._logTextview = self._builder.get_object("logTextview")
        self._robotIndicator = self._builder.get_object("robotIndicator")
        self._helmetIndicator = self._builder.get_object("helmetIndicator")
        self._joystickIndicator = self._builder.get_object("joystickIndicator")
        self._mainWindow.connect("delete-event", self.__delete_event)

        self._onoffButton.connect("toggled", self.__onoffButtonClick)
        self._settingsButton.connect("clicked", self.__settingsButtonClick)
        # self.printLog("*** Hello, I'm Johny! ***")

        try:
            self.setConfigurationFromFile(self._defaultConfigurationFilePath)
        except FileNotFoundError:
            self.printLog("Файл конфигурации по умолчанию не найден, проверьте его наличие или выберете другой")
        except:
            self.printLog("Ошибка чтения файла конфигурации, проверьте его корректность")
        else:
            self._onoffButton.set_property("sensitive", True)

        threading.Thread(daemon=True, target=self.__cyclicSending).start()  # запускаем поток циклических отправок данных
        self._mainWindow.show_all()
        Gtk.main()

    @property
    def isConnected(self):
        return self._isConnected

    def printLog(self, string):
        end_iter = self._logTextview.get_buffer().get_end_iter()  # получение итератора конца строки
        self._logTextview.get_buffer().insert(end_iter, str(datetime.datetime.now()) + "\t" + string + "\n")

    def __onoffButtonClick(self, w):
        state = w.get_active()
        if state:
            try:
                self.robot.connect()
                self.__robotOn()
                self._isConnected = True
            except ConnectionError:
                self.printLog("Не удается подключиться к роботу с адресом: " + self.robot.host.__repr__())
                w.set_active(False)
        else:
            try:
                self.__robotOff()
                self.robot.disconnect()
                self._isConnected = False
            except BrokenPipeError:
                self.printLog("Связь была прервана")

    def __settingsButtonClick(self, w):
        self._settingsButton.set_property("sensitive", False)
        _SettingsWindow(self)

    def __delete_event(self, widget, event, data=None):
        Gtk.main_quit()

    def setConfigurationFromFile(self, path):
        with open(path, "r") as file:
            self._configuration = json.load(file)
            try:
                self.robot.host = (self._configuration["ip"], self._configuration["port"])
            except KeyError:
                self.printLog("Файл конфигурации не содержит адрес робота")
                raise KeyError()

    def __robotOn(self):
        """ вызывается после соединения с роботом """
        self.robot.calibrateHead()
        self.robot.videoState(True)
        self._helmet.setZeroNow()

    def __robotOff(self):
        """ вызывается перед разъединением с роботом """
        self.robot.videoState(False)

    def __cyclicSending(self):
        while not self.__exit:
            if self._isConnected:
                try:
                    yaw, pitch, roll = self._helmet.getAngles()
                    self.robot.setHeadPosition(int(yaw), int(pitch), int(roll))
                except:
                    pass
                try:
                    pass    # TODO: управление с джойстика
                except:
                    pass
            time.sleep(0.1)
