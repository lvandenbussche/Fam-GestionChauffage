import network
import time


class ConnectWifi:
    def __init__(self, ssid, wifi_key):
        self.ssid = ssid
        self.password = wifi_key
        self.connected = False
        self.station = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

    def connect_wlan(self):

        self.station.active(True)
        self.connected = self.station.isconnected()
        if self.connected:
            print(
                "\nAlready Connected. Network config: %s"
                % repr(self.station.ifconfig())
            )
        else:
            print("Trying to connect to %s..." % self.ssid)
            self.station.connect(self.ssid, self.password)
            for retry in range(100):
                self.connected = self.station.isconnected()
                if self.connected:
                    break
                time.sleep(0.1)
                print(".", end="")
            if self.connected:
                print("\nConnected. Network config: %s" % repr(self.station.ifconfig()))
            else:
                print("\nFailed. Not Connected to: " + self.ssid)

    def disconnect_wlan(self):
        # Disconnect from the current network. You may have to
        # do this explicitly if you switch networks, as the params are stored
        # in non-volatile memory.
        if self.station.isconnected():
            print("Disconnecting...")
            self.station.disconnect()
        else:
            print("Wifi not connected.")

    def disable_wlan_ap(self):
        # Disable the built-in access point.
        self.ap.active(False)
        print("Disabled access point, network status is %s" % self.station.status())

