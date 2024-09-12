import time
import struct
from micropython import const

__version__ = "1.0.0"

# Bank 1
AUXID = 0x58  # AUXID    = 0b00001111
REVID = 0x59  # REVID    = 0b00000111
ID = 0x5A
CFG12 = 0x66

# Bank 0
ENABLE = 0x80
ATIME = 0x81
ASTEP = 0xD4
WTIME = 0x83
SP_TH = 0x84
STATUS = 0x93
ASTATUS = 0x94
DATA = 0x95
STATUS2 = 0x90
STATUS3 = 0x91
STATUS5 = 0xBB
STATUS4 = 0xBC
CFG0 = 0xBF
CFG1 = 0xC6
CFG3 = 0xC7
CFG6 = 0xF5
CFG8 = 0xC9
CFG9 = 0xCA
CFG10 = 0x65
PERS = 0xCF
GPIO = 0x6B
CFG20 = 0xD6
LED = 0xCD
AGC_GAIN_MAX = 0xD7
AZ_CONFIG = 0xDE
FD_TIME_1 = 0xE0
FD_TIME_2 = 0xE2
FD_CFG0 = 0xDF
FD_STATUS = 0xE3
INTERNAB = 0xF9
CONTROL = 0xFA
FIFO_MAP = 0xFC
FIFO_LVL = 0xFD
FDATA = 0xFE


HARDWARE_ID = const(0b10000001)

CFG0_LOW_POWER = const(0b00100000)
CFG0_BANK = const(0b00010000)
CFG0_WLONG = const(0b00000100)

CFG20_6_CH = const(0b00000000)
CFG20_12_CH = const(0b01000000)
CFG20_18_CH = const(0b01100000)

ENABLE_FDEN = const(0b01000000)
ENABLE_SMUXEN = const(0b00010000)
ENABLE_WEN = const(0b00001000)
ENABLE_SP_EN = const(0b00000010)
ENABLE_PON = const(0b00000001)

FD_CFG0_FIFO_WRITE = const(0b10000000)

FD_VALID = const(0b00100000)
FD_SAT = const(0b00010000)
FD_120HZ_VALID = const(0b00001000)
FD_100HZ_VALID = const(0b00000100)
FD_120HZ = const(0b00000010)
FD_100HZ = const(0b00000001)

INTERNAB_ASIEN = const(0b10000000)
INTERNAB_SP_IEN = const(0b00001000)
INTERNAB_FIEN = const(0b00000100)
INTERNAB_SIEN = const(0b00000001)

CONTROL_SW_RESET = const(0b00001000)
CONTROL_SP_MAN_AZ = const(0b00000100)
CONTROL_FIFO_CLR = const(0b00000010)
CONTROL_CLEAR_SAI_ACT = const(0b00000001)

FIFO_MAP_CH5 = const(0b01000000)
FIFO_MAP_CH4 = const(0b00100000)
FIFO_MAP_CH3 = const(0b00010000)
FIFO_MAP_CH2 = const(0b00001000)
FIFO_MAP_CH1 = const(0b00000100)
FIFO_MAP_CH0 = const(0b00000010)
FIFO_MAP_ASTATUS = const(0b00000001)

AZ_NEVER = const(0)
AZ_BEFORE_FIRST_CYCLE = const(255)


class AS7343:
    # Note that ASTATUS gets prepended to the FIFO data
    # And FD (Flicker Detect) gets appended.
    # For the sake of simplicity we don't enable these.
    CHANNEL_MAP = [
        "FZ", "FY", "FXL", "NIR", "VIS1_TL", "VIS1_BR",  # Cycle 1
        "F2", "F3", "F4", "F6", "VIS2_TL", "VIS2_BR",    # Cycle 2
        "F1", "F7", "F8", "F5", "VIS3_TL", "VIS3_BR",    # Cycle 3
    ]

    def __init__(self, i2c):
        self.address = 0x39
        self.i2c = i2c
        self.num_channels = 18
        self.active = False

        # Soft reset
        self.w_uint8(CONTROL, CONTROL_SW_RESET)
        time.sleep(0.5)

        # Bank 0
        self.w_uint8(CFG0, 0)

        # Set default AGAIN
        self.w_uint8(CFG1, 9)

        # Set default sensor settings
        self.set_gain(256)
        self.set_measurement_time(33)  # Roughly 30fps at 16ms/measurement
        self.set_integration_time(27800)
        self.set_channels(18)

        # Auto zero on measurement start
        self.w_uint8(AZ_CONFIG, AZ_BEFORE_FIRST_CYCLE)

        # Set the FIFO map
        self.w_uint8(
            FIFO_MAP,
            FIFO_MAP_CH5 | FIFO_MAP_CH4 | FIFO_MAP_CH3 | FIFO_MAP_CH2 | FIFO_MAP_CH1 | FIFO_MAP_CH0
        )

    def set_gain(self, gain):
        if gain == 0.5:
            bitlength = 0
        else:
            igain = int(gain)
            bitlength = 0
            while igain > 0:
                bitlength += 1
                igain >>= 1

        self.w_uint8(CFG1, bitlength)

    def set_measurement_time(self, measurement_time_ms):
        resolution = 2.78
        self.w_uint8(WTIME, int((measurement_time_ms - resolution) / resolution))

    def set_integration_time(self, integration_time_us, repeat=1):
        resolution = 2.78
        max_astep = (65534 + 1) * resolution

        if integration_time_us > max_astep:
            raise ValueError("Integration time out of range!")

        self.w_uint8(ATIME, repeat - 1)
        self.w_uint16(
            ASTEP, int((integration_time_us - resolution) / resolution) & 0xFFFE
        )

    def set_illumination_current(self, current):
        current = int((current - 4) / 2.0)
        temp = self.r_uint8(LED) & 0b10000000  # Preserve on/off state
        temp |= current & 0b01111111
        self.w_uint8(LED, temp)

    def set_illumination_led(self, state):
        temp = self.r_uint8(LED) & ~0b10000000  # Preserve current
        if state:
            temp |= 0b10000000
        self.w_uint8(LED, temp)

    def start_measurement(self):
        if self.active:
            return
        self.active = True
        # Enable things
        self.w_uint8(ENABLE, ENABLE_WEN | ENABLE_SMUXEN | ENABLE_SP_EN | ENABLE_PON)

    def stop_measurement(self):
        self.w_uint8(ENABLE, ENABLE_PON)
        self.w_uint8(CONTROL, CONTROL_FIFO_CLR)

    def force_autorange(self):
        self.w_uint8(CONTROL, CONTROL_SP_MAN_AZ)
        time.sleep(0.1)

    def set_channels(self, c):
        self.num_channels = c
        temp = self.r_uint8(CFG20) & ~CFG20_18_CH
        if c == 18:
            temp |= CFG20_18_CH
        if c == 12:
            temp |= CFG20_12_CH
        if c == 6:
            temp |= CFG20_6_CH
        self.w_uint8(CFG20, temp)

    def read_fifo(self):
        expected_results = self.num_channels
        results = []

        while self.r_uint8(FIFO_LVL) < expected_results:
            time.sleep(0.001)

        # Cycle 1 = FZ, FY, FXL, NIR, 2xVIS, FD
        # Cycle 2 = F2, F3, F4, F6, 2xVIS, FD
        # Cycle 3 = F1, F7, F8, F5, 2xVIS, FD
        while self.r_uint8(FIFO_LVL) > 0 and expected_results > 0:
            results.append(self.r_uint16(FDATA))
            expected_results -= 1

        return results

    def read(self):
        self.start_measurement()
        return dict(zip(self.CHANNEL_MAP, self.read_fifo()))

    def r_uint8(self, reg):
        self.i2c.writeto(self.address, bytes([reg]))
        return struct.unpack("<B", self.i2c.readfrom(self.address, 1))[0]

    def w_uint8(self, reg, value):
        self.i2c.writeto(self.address, bytes([reg, value]))

    def r_uint16(self, reg):
        self.i2c.writeto(self.address, bytes([reg]))
        return struct.unpack("<H", self.i2c.readfrom(self.address, 2))[0]

    def w_uint16(self, reg, value):
        self.i2c.writeto(self.address, struct.pack("<BH", reg, value))
