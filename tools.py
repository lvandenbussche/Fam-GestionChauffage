import time as time_
import flashbdev
import os



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


