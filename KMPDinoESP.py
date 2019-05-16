import machine
import ubinascii


# noinspection PyPep8Naming
class KMPDinoESP:
    DEBUG = False
    READ_CMD = 0x41
    WRITE_CMD = 0x40
    OLAT = 0X0A
    IODIRA = 0x00
    IODIRB = 0x01
    GPIO = 0x09

    # Relay Pins

    REL1PIN = 0x04
    REL2PIN = 0x05
    REL3PIN = 0x06
    REL4PIN = 0x07
    RELAY_COUNT = 4
    RELAY_PINS = [REL1PIN, REL2PIN, REL3PIN, REL4PIN]
    Relay = {
        'Relay1': 0x04,
        'Realy2': 0x05,
        'Relay3': 0x06,
        'Relay4': 0x07
    }

    IN1PIN = 0x00
    IN2PIN = 0x01
    IN3PIN = 0x02
    IN4PIN = 0x03
    OPTOIN_COUNT = 4
    OPTOIN_PINS = [IN1PIN, IN2PIN, IN3PIN, IN4PIN]
    OptoIn = {
        'OptoIn1': 0x00,
        'OptoIn2': 0x01,
        'OptoIn3': 0x02,
        'OptoIn4': 0x03
    }

    _expRxData = bytearray(8)

    def __init__(self):
        self.spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0)
        self.cs = machine.Pin(15, machine.Pin.OUT)
        self.cs.value(1)
        self.ExpanderInitGPIO()

    # *** Relays methods. ***

    def SetRelayState(self, relayNumber, state):
        if relayNumber > self.RELAY_COUNT - 1:
            return
        self.ExpanderSetPin(self.RELAY_PINS[relayNumber], state)

    def SetRelayStateByname(self, relayName, state):
        for key, val in self.Relay.items():
            if key == relayName:
                self.ExpanderSetPin(val, state)
        return

    def GetRelayState(self, relayNumber):
        if relayNumber > self.RELAY_COUNT - 1:
            return False
        relay_state = self.ExpanderGetPin(self.RELAY_PINS[relayNumber])
        if relay_state != 0:
            relay_state = 1
        else:
            relay_state = 0
        return relay_state

    # *** Opto input methods. ***

    def GetOptoInState(self, optoInNumber):
        if optoInNumber > self.OPTOIN_COUNT - 1:
            return False
        return self.ExpanderGetPin(self.OPTOIN_PINS[optoInNumber])

    # *** Expander MCP23S17 methods. ***

    def ExpanderInitGPIO(self):
        for pin in self.RELAY_PINS:
            if self.DEBUG: print('Initialisation Pin Relay : {}'.format(pin))
            self.ExpanderSetDirection(pin, 'OUTPUT')

        for pin in self.OPTOIN_PINS:
            if self.DEBUG: print('Initialisation Opto Pin : {}'.format(pin))
            self.ExpanderSetDirection(pin, 'INPUT')

    def ExpanderSetPin(self, pinNumber, state):
        if self.DEBUG: print('ExpanderSetPin - Set Pin Relay : {}'.format(pinNumber))
        if self.DEBUG: print('ExpanderSetPin - Read Register')
        registerData = self.ExpanderReadRegister(self.OLAT)
        if self.DEBUG: print('ExpanderSetPin - RegisterData : {}'.format(registerData))

        if state:
            if self.DEBUG: print('ExpanderSetPin - State = True')
            registerData |= (1 << pinNumber)
            if self.DEBUG: print('ExpanderSetPin - RegisterData : {}'.format(registerData))
        else:
            if self.DEBUG: print('ExpanderSetPin - State = False')
            registerData &= ~(1 << pinNumber)
            if self.DEBUG: print('ExpanderSetPin - RegisterData : {}'.format(registerData))

        if self.DEBUG: print('ExpanderSetPin - Write in registre : {} - {}'.format(self.OLAT, bin(registerData)))
        self.ExpanderWriteRegister(self.OLAT, registerData)

    def ExpanderSetDirection(self, pinNumber, mode):

        if mode == 'INPUT':
            if self.DEBUG: print('ExpanderSetDirection - Read Register')
            registerData = self.ExpanderReadRegister(self.IODIRB)
            if self.DEBUG: print('ExpanderSetDirection - RegisterData : {}'.format(registerData))
            registerData |= (1 << pinNumber)
            if self.DEBUG: print('ExpanderSetDirection - Mode INPUT : {}'.format(registerData))
            self.ExpanderWriteRegister(self.IODIRB, registerData)
        else:
            if self.DEBUG: print('ExpanderSetDirection - Read Register')
            registerData = self.ExpanderReadRegister(self.IODIRA)
            if self.DEBUG: print('ExpanderSetDirection - RegisterData : {}'.format(registerData))
            registerData &= ~(1 << pinNumber)
            if self.DEBUG: print('ExpanderSetDirection - Mode OUTPUT : {}'.format(registerData))
            self.ExpanderWriteRegister(self.IODIRA, registerData)

    def ExpanderGetPin(self, pinNumber):
        registerData = self.ExpanderReadRegister(self.GPIO)
        if self.DEBUG: print('ExpanderGetPin - registerData : {}'.format(registerData))
        return registerData & (1 << pinNumber)

    def ExpanderReadRegister(self, address):
        txData = bytearray(2)
        txData[0] = self.READ_CMD
        txData[1] = address
        if self.DEBUG: print('ExpanderReadRegister - CMD : {} - ADRR : {}'.format(hex(self.READ_CMD), hex(address)))
        self.cs.value(0)
        self.spi.write(txData)
        self.spi.readinto(self._expRxData)
        self.cs.value(1)
        if self.DEBUG: print(
            'ExpanderReadRegister read to register value : {}'.format(ubinascii.hexlify(self._expRxData)))
        return self._expRxData[0]

    def ExpanderWriteRegister(self, address, data):
        if address == self.IODIRA or address == self.IODIRB:
            txData = bytearray(8)
        else:
            txData = bytearray(3)

        txData[0] = self.WRITE_CMD
        txData[1] = address
        txData[2] = data
        if self.DEBUG: print('ExpanderWriteRegister write to regsiter value : {}'.format(ubinascii.hexlify(txData)))
        self.cs.value(0)
        self.spi.write(txData)
        self.cs.value(1)
