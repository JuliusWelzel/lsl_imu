from time import sleep  # not used
import pylsl        # not used,
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
import qwiic_button
import imusensor


if __name__ == '__main__':
    # TODO: update README.md with changed example_usage file!
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
    imu_out = imusensor.create_lsl_stream(100)  # create LSL stream for IMU
    btn.clear_event_bits()
    flag_btn = False

    while not flag_btn:

        btn.LED_config(70, 3000, 1000)
        flag_btn = btn.has_button_been_clicked()
        if flag_btn:
            imusensor.send_imu_data_to_lsl(imu_out, btn)
            flag_btn = False
