# AS7343 MicroPython

A MicroPython library for the AS7343 14-channel spectral sensor.

AS7343 is a 14-channel multi-purpose spectral sensor. It can detect 14 spectral channels - 12 in the visible spectrum (VIS) to near-infrared (NIR) range, a clear channel and flicker channel.

You can buy our AS7343 breakout [here](https://shop.pimoroni.com/products/as7343-14-channel-multi-spectral-sensor-breakout)!

- [AS7343 MicroPython](#as7343-micropython)
  - [Installing](#installing)
    - [mip](#mip)
  - [Usage](#usage)
    - [Function Reference](#function-reference)
      - [set\_gain](#set_gain)
      - [set\_measurement\_time](#set_measurement_time)
      - [set\_integration\_time](#set_integration_time)
      - [set\_illumination\_current](#set_illumination_current)
      - [set\_illumination\_led](#set_illumination_led)
      - [start\_measurement](#start_measurement)
      - [stop\_measurement](#stop_measurement)
      - [read](#read)
      - [read\_fifo](#read_fifo)
  - [Hardware Details](#hardware-details)
    - [Overview](#overview)
    - [Channels](#channels)

## Installing

### mip

If your board is online and has `mip` you should be able to run:

```python
import mip
mip.install("github:org/pimoroni/as7343-micropython/package.json")
```

Otherwise, using Tools -> Manage Packages in Thonny, locate the
`as7343-micropython` package and install it as normal.

## Usage

Basic example:

```python
from as7343 import AS7343
from machine import I2C

i2c = machine.I2C(id=0, sda=20, scl=21)
as7343 = AS7343(i2c)

while True:
    readings = as7343.read()
    print(readings)
```

### Function Reference

#### set_gain

Internally this sets `AGAIN` on the `CFG1` register, which changes the
spectral engines gain setting.

Valid values are 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 and 2048.

#### set_measurement_time

Set the total measurement time, this includes the integration time and the
wait between readings.

Time is given in milliseconds and values from 

#### set_integration_time

Set the portion of the measurement time which is actually used for sensor
integration. This must be less than the total measurement time.

Time is given in microseconds, and longer times will increase the data output
values and sensitivity of the sensor.

The granularity is 2.78us, and values up to 182,187us (182ms or roughly
1/5th a second) are supported.

The `repeat` (internally known as `ASTEP`) argument supports values from
1 to 256 and acts as a multiplier for the time.

The full scale ADC value is given as roughly:

```python
repeat * integration_time_us
```

#### set_illumination_current

Set the current of the illumination LEDs.

Valid values are 4mA up to 258mA with increments of 2mA.

#### set_illumination_led

Enable the illumination LEDs, takes one value: `True` for on and `False` for
off.

#### start_measurement

Flip the `SMUXEN` bit to start measurements into the internal FIFO.

This is done automatically the first time you call `read()`.

#### stop_measurement

Clear the `SMUXEN` bit, stopping measurements. You should do this before
changing gain and measurement settings.

#### read

Starts measurements (if they are stopped) and returns a dict contianing the
sensor readings. By default this includes all eighteen channels from three
read cycles.

#### read_fifo

Attempts to read a full set of data from the FIFO and returns the raw read
results as a list in the order:

```
FZ, FY, FXL, NIR, VIS_TL, VIS_BR, FD
F2, F3, F4,  F6,  VIS_TL, VIS_BR, FD
F1, F7, F8,  F5,  VIS_TL, VIS_BR, FD
```

A list with this order is provided as `AS7343.CHANNEL_MAP`

## Hardware Details

### Overview

Uses six 16-bit ADCs switched over the 5x5 array via SMUX
and then output sequentially into the 18-entry, 16-bit data registers.

### Channels

Values for AGAIN 1024x, Integration Time: 27.8ms.

| Chan | From | To   | Min  | Typ   | Max   | Colour     |
|------|------|------|------|-------|-------|------------|
| F1   | 395  | 415  | 4311 | 5749  | 7186  | Violet     |
| F2   | 415  | 435  | 1317 | 1756  | 2196  | Violet     |
| FZ   | 440  | 460  | 1627 | 2169  | 2711  | Blue       |
| F3   | 465  | 485  | 577  | 770   | 962   | Blue/Cyan  |
| F4   | 506  | 525  | 2356 | 3141  | 3926  | Cyan       |
| FY   | 545  | 565  | 2810 | 3747  | 4684  | Green      |
| F5   | 540  | 550  | 1180 | 1574  | 1967  | Yellow/Grn |
| FXL  | 590  | 610  | 3582 | 4776  | 5970  | Orange     |
| F6   | 630  | 650  | 2502 | 3336  | 4170  | Orange/Red |
| F7   | 680  | 700  | 4095 | 5435  | 6774  | Red        |
| F8   | 735  | 745  | 648  | 864   | 1080  | Red        |
| NIR  | 845  | 855  | 7936 | 10581 | 13226 | Infra-Red  |

Irradiance responsivity values from figure 8.

Approximate colours from Figure 11.