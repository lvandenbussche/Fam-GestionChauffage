import time as time_
import flashbdev
import os
import machine



class Tools:

    @staticmethod
    def write_data(name, value):
        try:
            with open(name, "w") as f:
                f.write(str(value))
        except OSError:
            print("Can't write to file %s" % name)

    @staticmethod
    def read_data(name):
        try:
            with open(name) as f:
                v = int(f.read())
        except OSError:
            v = 0
            try:
                with open(name, "w") as f:
                    f.write(str(v))
            except OSError:
                print("Can't create file %s" % name)

        except ValueError:
            print("invalid data in file %s" % name)
            v = 0

        return v

    @staticmethod
    def millis():
        return int(round(time_.time() * 1000))

    @staticmethod
    def format():
        os.VfsFat.mkfs(flashbdev.bdev)


class WDT:
    def __init__(self, id=0, timeout=120):
        self._timeout = timeout / 10
        self._counter = 0
        self._timer = machine.Timer(id)
        self.init()

    def _wdt(self, t):
        self._counter += self._timeout
        if self._counter >= self._timeout * 10:
            machine.reset()

    def feed(self):
        self._counter = 0

    def init(self, timeout=None):
        timeout = timeout or self._timeout
        self._timeout = timeout
        self._timer.init(period=int(self._timeout * 1000), mode=machine.Timer.PERIODIC, callback=self._wdt)

    def deinit(self):  # will not stop coroutine
        self._timer.deinit()


