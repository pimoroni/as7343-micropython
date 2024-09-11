from as7343 import AS7343
from pimoroni_i2c import PimoroniI2C
from picographics import PicoGraphics, DISPLAY_PICO_W_EXPLORER, PEN_P4
from pimoroni import Button
import time

# Edits by Tony Abbey 20240909 with button Y to toggle between channel
# and wavelength labels, and display  the unscaled values above the bar
# graphs when in wavelength mode. Max values tweaked to give  a more even
# set of bars with LED on a white paper reflection.

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
#f1 7186, greater
#f5 1967, greater gain
#f3 962, lower gain
#f4 3926, higher gain
#f3 2600, lower gain
#FZ 2711, lower gain
#FXL 5970, higher gain
#F6 4170, lower gain
#F7 6774, higher gain
#F8 1080, lower gain
MAX_VALUES = [
    500,
    668,
    3200,
    3000,
    4000,
    6000,
    1600,
    6000,
    5500,
    4400,
    2000,
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
ORDER2 = [
    "405",
    "425",
    "450",
    "475",
    "515",
    "550",
    "555",
    "600",
    "640",
    "690",
    "745",
    "855"
]

MARGIN = max([display.measure_text(l) for l in ORDER]) + 2

BAR_WIDTH = 16
BAR_SPACING = 4
BAR_HEIGHT = WIDTH - MARGIN

OFFSET_LEFT = int((HEIGHT - 110 - ((BAR_WIDTH + BAR_SPACING) * 12)) / 2)

WHICH_LABEL = 0

while True:
    display.set_pen(0)
    display.clear()
    readings = as7343.read()

    for i, label in enumerate(ORDER):
        reading = readings[label]
        if reading > MAX_VALUES[i]:
          print (label,reading,MAX_VALUES[i]) # show gain control in action
        MAX_VALUES[i] = max(reading, MAX_VALUES[i])  # AGC removed
        scaled = int(reading / MAX_VALUES[i] * BAR_HEIGHT)
        y = (i + 1) * (BAR_WIDTH + BAR_SPACING)
        y += OFFSET_LEFT

        display.set_pen(i + 1)
        display.rectangle(MARGIN, y, scaled, BAR_WIDTH)

        display.set_pen(WHITE)
        if WHICH_LABEL == 0:
            display.text(label, 0, y + 1)
        else:
            display.text(ORDER2[i], 0, y + 1)
            display.text(str(reading), scaled+35, y + 1)

    display.update()

    if button_b.is_pressed:
        as7343.set_illumination_led(False)

    elif button_a.is_pressed:       
        as7343.set_illumination_current(4)
        as7343.set_illumination_led(True)

    elif button_x.is_pressed:
        as7343.set_illumination_current(10)
        as7343.set_illumination_led(True)

    elif button_y.is_pressed:
        WHICH_LABEL = not WHICH_LABEL
        time.sleep(0.5)

    time.sleep(0.01)
