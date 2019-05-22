import ConnectWiFi
import webrepl
import time


W = ConnectWiFi.ConnectWifi('101', 'wifigest')
W.connect_wlan()
W.disable_wlan_ap()
time.sleep(2)

webrepl.start()

