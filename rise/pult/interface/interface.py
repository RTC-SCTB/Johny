import json
import datetime
import gi

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
        self._settingsWindow.connect("delete-event", self.__delete_event)
        self._settingsWindow.show_all()

    def __calibrateButtonClick(self, w):
        pass

    def __videoSwitchClick(self, w, state):
        pass

    def __confFilePathChange(self, w):
        try:
            self._owner.setConfigurationFromFile(w.get_uri()[6:])
            self._owner._onoffButton.set_property("sensitive", True)
        except:
            self._owner.printLog("Ошибка чтения файла конфигурации, проверьте его корректность")

    def __delete_event(self, widget, event, data=None):
        self._owner._settingsButton.set_property("sensitive", True)


class Pult:
    def __init__(self):
        """ развертываем интерфейс из glade """
        self._defaultConfigurationFilePath = "conf.json"
        self._configuration = None

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

        self._onoffButton.connect("clicked", self.__onoffButtonClick)
        self._settingsButton.connect("clicked", self.__settingsButtonClick)
        # self.printLog("*** Hello, I'm Johny! ***")

        try:
            self.setConfigurationFromFile(self._defaultConfigurationFilePath)
            self._onoffButton.set_property("sensitive", True)
        except FileNotFoundError:
            self.printLog("Файл конфигурации по умолчанию не найден, проверьте его наличие или выберете другой")
        except:
            self.printLog("Ошибка чтения файла конфигурации, проверьте его корректность")

        self._mainWindow.show_all()
        Gtk.main()

    def printLog(self, string):
        end_iter = self._logTextview.get_buffer().get_end_iter()  # получение итератора конца строки
        self._logTextview.get_buffer().insert(end_iter, str(datetime.datetime.now()) + "\t" + string + "\n")

    def __onoffButtonClick(self, w):
        pass

    def __settingsButtonClick(self, w):
        self._settingsButton.set_property("sensitive", False)
        _SettingsWindow(self)

    def __delete_event(self, widget, event, data=None):
        Gtk.main_quit()

    def setConfigurationFromFile(self, path):
        with open(path, "r") as file:
            self._configuration = json.load(file)

