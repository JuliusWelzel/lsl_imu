from time import sleep          #import
import pylsl
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
import qwiic_button

def createLsLStream(imu_srate):
    srate = imu_srate
    name = 'MPU6050LSL'
    stream_type = 'IMU'
    channel_names = ["AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ"]
    n_channels = len(channel_names)

    # first create a new stream info
    info = pylsl.StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid2424')

    # next make an outlet; we set the transmission chunk size to 32 samples and
    # the outgoing buffer size to 360 seconds (max.)
    imu_out = pylsl.StreamOutlet(info, 32, 360)

    return imu_out


def sendImuDataToLsL(imu_out,btn):

    btn.LED_config(120,1000,0)
    btn.clear_event_bits()
    flag_btn = False

    start_time = pylsl.local_clock()
    sent_samples = 0
    print (" Reading Data of Gyroscope and Accelerometer")


    while not flag_btn: #sent data for 10s

        elapsed_time = pylsl.local_clock() - start_time
        required_samples = int(imu_srate * elapsed_time) - sent_samples

        if required_samples > 0:
        # make a chunk==array of length required_samples, where each element in the array
        # is a new random n_channels sample vector

            #Read Accelerometer raw value
            acc = sensor.acceleration

            #Read Gyroscope raw value
            gyro = sensor.gyro

            stamp   = pylsl.local_clock()
            mychunk = [list(acc + gyro)]
            imu_out.push_chunk([list(acc + gyro)], stamp)
            sent_samples += required_samples

        flag_btn = btn.has_button_been_clicked()


    if flag_btn:
        btn.LED_off()
        btn.clear_event_bits()
        print ("Stop sendig data of Gyroscope and Accelerometer")
        btn.LED_config(100, 4,1)
