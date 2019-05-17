from mqtt_as import MQTTClient, config
import uasyncio as asyncio
from KMPDinoESP import KMPDinoESP
from utime import ticks_ms, ticks_diff
import tools
import ubinascii
import dht as dht22
import machine
import time
import gc


MQTTClient.DEBUG = True
QOS = 1

MQTTSERVER = '192.168.0.246'
PUB_TOPIC_TEMP = '/ESP/KMP/Node1/temp'
PUB_TOPIC_HUM = '/ESP/KMP/Node1/hum'
PUB_TOPIC_MOTION = '/ESP/KMP/Node1/motion'
PUB_TOPIC_DEBUG = '/ESP/KMP/Node1'
SUB_TOPIC = ['/ESP/KMP/Node1/consigne', '/ESP/KMP/Node1/relay']

GPIO_EXTENDER = KMPDinoESP()
RELAYS_CHAUFFAGE = 0
DHT = dht22.DHT22(machine.Pin(5))
PIN_MOTION = 4
MOTION = machine.Pin(PIN_MOTION, machine.Pin.IN)
MOTION_INTERVAL = 10000


class KMPNode(MQTTClient):
    def __init__(self):
        # ** init MQTTClient **
        config['ssid'] = None
        config['wifi_pw'] = None
        config['server'] = MQTTSERVER
        config['client_id'] = ubinascii.hexlify(machine.unique_id())
        config['subs_cb'] = self.mqtt_receive_cb
        config['wifi_coro'] = self.wifi_state_cb
        config['connect_coro'] = self.mqtt_connect_cb
        config['clean'] = False
        config['clean_init'] = False
        super().__init__(config)
        # ** init KMPNode **
        self.internet_outage = True
        self.internet_outages = 0
        self.internet_outage_start = ticks_ms()
        self.loop = asyncio.get_event_loop()
        self.tools = tools.Tools()
        self.temp = None
        self.hum = None
        self.consigne = 0
        self._start()

    def _start(self):
        self.loop.create_task(self._coro_temp())
        self.loop.create_task(self._coro_motion())
        self.loop.run_until_complete(self._main_loop())

    async def _connect_brooker(self):
        conn = False
        while not conn:
            await self.connect()
            conn = True
        self.internet_outage = False

# ** Publish a message if WiFi and broker is up, else discard **
    async def _publish_msg(self, topic, msg):
        self.dprint("{} - Publishing message on topic {}: {}".format(time.time(), topic, msg))
        if not self.internet_outage:
            await self.publish(topic, msg)
        else:
            self.dprint("Message was not published - no internet connection")

    async def publish_debug_msg(self, subtopic, msg):
        await self._publish_msg("{}/{}".format(PUB_TOPIC_DEBUG, subtopic), str(msg))

# ** function callback **
    async def wifi_state_cb(self, state):  # Function CallBack (Wifi state change)
        self.internet_outage = not state
        if state:
            self.dprint('WiFi is up.')
            duration = ticks_diff(ticks_ms(), self.internet_outage_start) // 1000
            self.dprint('ReconnectedAfter', duration)
        else:
            self.internet_outages += 1
            self.internet_outage_start = ticks_ms()
            self.dprint('WiFi is down.')
        await asyncio.sleep(1)

    async def mqtt_connect_cb(self, client):  # Function CallBack (Brooker connected)
        if len(SUB_TOPIC) > 1:
            for topic in SUB_TOPIC:
                await self.subscribe(topic, QOS)
                self.dprint('subscribe topic : {}'.format(topic))
        else:
            self.dprint('subscribe topic : {}'.format(SUB_TOPIC[0]))
            await self.subscribe(SUB_TOPIC[0], QOS)

    def mqtt_receive_cb(self, topic, msg):  # Function CallBack (Receive Message)
        topic_str = str(topic, 'utf8')
        msg_str = str(msg, 'utf8')
        self.dprint("Received MQTT message topic={}, msg={}".format(topic_str, msg))

        if topic_str == SUB_TOPIC[1]:
            if msg_str == 'ON':
                GPIO_EXTENDER.SetRelayState(RELAYS_CHAUFFAGE, 1)
            else:
                GPIO_EXTENDER.SetRelayState(RELAYS_CHAUFFAGE, 0)

# ** Coroutine function ***

    async def _coro_temp(self):
        while True:
            DHT.measure()
            await asyncio.sleep(2)
            self.temp = DHT.temperature()
            self.hum = DHT.humidity()
            await self._publish_msg(PUB_TOPIC_TEMP, str(self.temp))
            await self._publish_msg(PUB_TOPIC_HUM, str(self.hum))
            await asyncio.sleep(30)

    async def _coro_motion(self):
        motion_detected = False

        while True:
            if MOTION.value() == 1 and motion_detected == 0:
                self.dprint('Motion Detected')
                motion_detected = True
                await self._publish_msg(PUB_TOPIC_MOTION, str(1))
                start = self.tools.millis()
            if MOTION.value() == 0 and motion_detected == 1:
                if self.tools.millis() - start >= MOTION_INTERVAL:
                    motion_detected = 0
                    await self._publish_msg(PUB_TOPIC_MOTION, str(0))
            await asyncio.sleep(1)

    async def _main_loop(self):
        await self._connect_brooker()
        mins = 0
        while True:
            gc.collect()  # For RAM stats.
            mem_free = gc.mem_free()
            mem_alloc = gc.mem_alloc()
            try:
                await self.publish_debug_msg("Uptime", mins)
                await self.publish_debug_msg("Outages", self.internet_outages)
                await self.publish_debug_msg("MemFree", mem_free)
                await self.publish_debug_msg("MemAlloc", mem_alloc)
            except Exception as e:
                self.dprint("Exception occurred: ", e)
            mins += 1

            await asyncio.sleep(60)



