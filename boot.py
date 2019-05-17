import ConnectWiFi

W = ConnectWiFi.ConnectWifi('101', 'wifigest')
W.connect_wlan()
W.disable_wlan_ap()

import webrepl
webrepl.start()

