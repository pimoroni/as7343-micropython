from as7343 import AS7343
from pimoroni_i2c import PimoroniI2C
from picographics import PicoGraphics, DISPLAY_PICO_W_EXPLORER, PEN_P4
from pimoroni import Button
import time

i2c = PimoroniI2C(sda=20, scl=21)
as7343 = AS7343(i2c)

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

display = PicoGraphics(display=DISPLAY_PICO_W_EXPLORER, pen_type=PEN_P4, rotate=270)
display.set_font("bitmap8")
display.set_backlight(0.5)

WIDTH, HEIGHT = display.get_bounds()

BLACK = display.create_pen(0, 0, 0)

F1 = display.create_pen(130, 0, 200)
F2 = display.create_pen(84, 0, 255)
FZ = display.create_pen(0, 70, 255)
F3 = display.create_pen(0, 192, 255)
F4 = display.create_pen(31, 255, 0)
FY = display.create_pen(179, 255, 0)
F5 = display.create_pen(163, 255, 0)
FXL = display.create_pen(255, 190, 0)
F6 = display.create_pen(255, 33, 0)
F7 = display.create_pen(255, 0, 0)
F8 = display.create_pen(171, 0, 0)
NIR = display.create_pen(97, 0, 0)

WHITE = display.create_pen(255, 255, 255)

# Starting max values for auto-ranging
MAX_VALUES = [
    7186,
    2196,
    2711,
    962,
    3926,
    4684,
    1967,
    5970,
    4170,
    6774,
    1080,
    13226
]

# List order for values
ORDER = [
    "F1",
    "F2",
    "FZ",
    "F3",
    "F4",
    "FY",
    "F5",
    "FXL",
    "F6",
    "F7",
    "F8",
    "NIR"
]

MARGIN = max([display.measure_text(l) for l in ORDER]) + 2

BAR_WIDTH = 16
BAR_SPACING = 4
BAR_HEIGHT = WIDTH - MARGIN

OFFSET_LEFT = int((HEIGHT - 110 - ((BAR_WIDTH + BAR_SPACING) * 12)) / 2)

while True:
    display.set_pen(0)
    display.clear()
    readings = as7343.read()

    for i, label in enumerate(ORDER):
        reading = readings[label]

        MAX_VALUES[i] = max(reading, MAX_VALUES[i])
        scaled = int(reading / MAX_VALUES[i] * BAR_HEIGHT)
    
        y = (i + 1) * (BAR_WIDTH + BAR_SPACING)
        y += OFFSET_LEFT

        display.set_pen(i + 1)
        display.rectangle(MARGIN, y, scaled, BAR_WIDTH)

        display.set_pen(WHITE)
        display.text(label, 0, y + 1)

    display.update()

    if button_b.is_pressed:
        as7343.set_illumination_led(False)

    elif button_a.is_pressed:       
        as7343.set_illumination_current(4)
        as7343.set_illumination_led(True)

    elif button_x.is_pressed:
        as7343.set_illumination_current(10)
        as7343.set_illumination_led(True)

    time.sleep(0.01)
