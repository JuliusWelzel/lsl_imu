# mediapipe to lsl streaming

import mediapipe as mp

import pylsl as lsl
import numpy as np
import sys
import cv2
import pyxdf
from time import sleep, time
import matplotlib.pyplot as plt
from threading import Thread, Event


class MediaPipeLsLStreamer:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.1):

        # when the mediapipe is first started, it detects the hands. After that it tries to track the hands
        # as detecting is more time consuming than tracking. If the tracking confidence goes down than the
        # specified value then again it switches back to detection
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
        )
        # add cfg params
        self.cfg_ch_nms = mp_hand_labels()

        # prelocate vars
        self.pre_acc = 0
        self.pre_lb = [""]
        self.pre_pos = np.empty((self.cfg_ch_nms.shape))
        self.pre_pos[:] = np.nan

    def start_lsl(self, name="MP_hands", stream_type="motion"):

        n_channels = len(medpi.cfg_ch_nms)
        srate = 24
        info = lsl.StreamInfo(
            name, stream_type, n_channels, srate, "float32", "uid2030"
        )

        # # append some meta-data
        # chns = info.desc().append_child("channels")
        # for chan_ix, label in enumerate(self.cfg_ch_nms):
        #     ch = chns.append_child("channel")
        #     ch.append_child_value("label", label)
        #     ch.append_child_value("unit", "pixel")
        #     ch.append_child_value("type", "Motion")

        self.lsl_outlet = lsl.StreamOutlet(info, n_channels)

    def sent_to_lsl(self):

        # For webcam input:
        srate = 24
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, srate)
        print("Start recording")

        start_time = lsl.local_clock()
        sent_samples = 0
        while True:
            elapsed_time = lsl.local_clock() - start_time
            required_samples = int(srate * elapsed_time) - sent_samples
            if required_samples > 0:
                success, image = self.cap.read()
                if not success:
                    print("No image read")
                    continue

                tmp_pos, tmp_acc, tmp_lab = find_handlandmarks_online(self, image)
                t_ = list(tmp_pos)
                self.lsl_outlet.push_sample(t_)

            if cv2.waitKey(5) & 0xFF == 27:
                break
                self.cap.release()
                cv2.destroyAllWindows()
                self.lsl_outlet.close()

        print("Recording done")
        self.cap.release()
        cv2.destroyAllWindows()

    def stop_record(self):
        self.cap.release()


def find_handlandmarks_online(mp_class, tmp_image):
    """
        This functions finds the coordinates of all hand landmarks in a single image/frame
        """
    # utls for drawing hand online
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands
    flag_hand_detect = True

    # prep image via cv and process via MP (self.hands)
    tmp_image.flags.writeable = False
    tmp_image = cv2.cvtColor(tmp_image, cv2.COLOR_BGR2RGB)
    results = mp_class.hands.process(tmp_image)

    if not results.multi_hand_landmarks:
        tmp_pos = mp_class.pre_pos
        tmp_acc = mp_class.pre_acc
        tmp_lab = mp_class.pre_lb
        flag_hand_detect = False

        return tmp_pos, tmp_acc, tmp_lab

    # check if output from mp processing is something
    tmp_lab = results.multi_handedness[0].classification[0].label
    tmp_pos_mp = []

    for idx_lm, lms in enumerate(results.multi_hand_landmarks[0].landmark):
        # landMark holds x,y,z ratios of single landmark
        x, y, z = lms.x, lms.y, lms.z
        tmp_pos_mp.append([x, y, z])
        tmp_acc = results.multi_handedness[0].classification[0].score

    tmp_pos = np.asarray(tmp_pos_mp).flatten()

    for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            tmp_image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style(),
        )
        # Flip the image horizontally for a selfie-view display.
        tmp_image = cv2.resize(tmp_image, (1280, 960))
        cv2.imshow(
            "MediaPipe Hands", cv2.flip(cv2.cvtColor(tmp_image, cv2.COLOR_RGB2BGR), 1)
        )
        if cv2.waitKey(5) & 0xFF == 27:
            cv2.destroyAllWindows()
            mp_class.cap.release()

    return tmp_pos, tmp_acc, tmp_lab


def mp_hand_labels():
    """
    Input : None

    Returns
    -------
    mp_labels : character string
        MediaPipe labels 0-63 as vector.

    """

    hand_points = np.arange(0, 21)  # number of tracked points
    dims = ["x", "y", "z"]  # dimensions in which hand is tracked
    labels = [str(h) + d for h in hand_points for d in dims]
    mp_labels = np.array(labels)
    return mp_labels


medpi = MediaPipeLsLStreamer(max_num_hands=1)
medpi.start_lsl()
medpi.sent_to_lsl()
medpi.stop_record()

data, hd = pyxdf.load_xdf(r"C:\Users\juliu\Desktop\test_mp.xdf")
tmp_ts = data[0]["time_series"][:, 0::3]

plt.plot(tmp_ts)
