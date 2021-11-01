# LSL IMU   
The repo provides a first rough draft of an setup in which data from a [IMU](https://medium.com/@niru5/intro-to-inertial-measurement-unit-imu-part-1-47f19fc7d68d) is streamed via a raspberry pi and python to [LSL](https://labstreaminglayer.readthedocs.io/index.html).

# Pre-requisites
List of hardware
- Raspberry Pi 4 (rpi)
- [6 DOF IMU (ISM330DLC)](https://www.st.com/resource/en/datasheet/ism330dlc.pdf)
- [QwiicPiHat](https://www.sparkfun.com/products/14459)
- QwiicCable
- (optinal) [QwiicButton](https://www.sparkfun.com/products/16842)

## Raspberry Pi
Some of the requirements are to enable I2C in rpi.
Installing I2C tools and smbus
```bash
sudo apt-get install i2c-tools
sudo pip install smbus
```
Connect the QwiicPiHat to the rpi. The ISM330DLC and the LED button are connected with the QwiicPiHat via a cable.

After you have made the connections, type the following command -
```bash
sudo i2cdetect -y 1
```
If you see 68 in the output, then that means the sensor is connected to the rpi and 68 is the address of the sensor.

# Basic Usage
The below code is a basic starter for the project.
```python
from time import sleep
import pylsl
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
import qwiic_button

from imusensor import imu


# button config
btn = qwiic_button.QwiicButton()
btn.LED_off()

# board config
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = ISM330DHCX(i2c)

# lsl config
imu_srate = 100

# run streams depending on button status
# click to start streaming to LSL
# click again to stop stream
imu_out = imu.createLsLStream(100) # create LSL stream for IMU
btn.clear_event_bits()
flag_btn = False

while not flag_btn:

    btn.LED_config(70,3000,1000)
    flag_btn = btn.has_button_been_clicked()
    if flag_btn:
        imu.sendImuDataToLsL(imu_out,btn)
        flag_btn = False
```

This is what the LSL streams would look like. 6 channels displayed represent the x-y-z component of the Accelerometer and Gyroscope respectively.

![](lsl_streams.gif)

## ToDo's
- [ ] add calibration
- [ ] implement online filter options
- [ ] optimise repo setuptools
- [ ] add support for additional IMUs

v0.1.0
