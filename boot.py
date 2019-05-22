import ConnectWiFi
import webrepl
import time


W = ConnectWiFi.ConnectWifi('Reseau Wi-Fi de Lionel', 'Klat0Verata')
W.connect_wlan()
W.disable_wlan_ap()
time.sleep(2)

webrepl.start()

