import subprocess


class VideoProcess:
    def __init__(self):
        self._process = None
        self._isConnected = False

    def start(self, l):
        if self._isConnected:
            return
        self._isConnected = True
        self._process = subprocess.Popen(l, stdout=subprocess.PIPE)

    def stop(self):
        if not self._isConnected:
            return
        self._isConnected = False
        self._process.terminate()
