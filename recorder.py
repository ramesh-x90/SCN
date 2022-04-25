from datetime import datetime
import time
import ffmpeg

import numpy as np
from getScreen import Capture
import os
import timeit
from PyQt5.QtCore import QThread
import cv2
from PyQt5 import QtCore
import subprocess as sp
from PIL import Image

FPS = 10


class reCorder(QThread):
    frame = QtCore.pyqtSignal(int)
    finishedSingnl = QtCore.pyqtSignal()

    def __init__(self, resolutionindex: int, hwndRef: list) -> None:

        super().__init__()
        self.running = True
        self.paused = False
        self.res = resolutionindex
        self.bitrate = "200k"
        self.hwndref = hwndRef

    def setBitRtate(self, index: int):
        if index == 1:
            self.bitrate = "300k"
        elif index == 2:
            self.bitrate = "400k"
        elif index == 3:
            self.bitrate = "500k"

    def run(self) -> None:
        i = 0

        FHD = [1920, 1080]
        HD = [1080, 720]

        width = HD[0]
        height = HD[1]

        if self.res == 1:
            width = FHD[0]
            height = FHD[1]

        path = 'recordings'

        try:
            os.mkdir(path)
        except FileExistsError as e:
            pass

        fileName = f"{path}/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f') }.mp4"

        # fourcc = cv2.VideoWriter_fourcc(*'H264')

        # out = cv2.VideoWriter(
        #     fileName, fourcc, FPS, (width, height))

        cmd_out = ['ffmpeg',
                   '-y',  # (optional) overwrite output file if it exists
                   '-f', 'image2pipe',
                   '-vcodec', 'mjpeg',
                   '-r', str(FPS),  # frames per second
                   '-i', '-',  # The input comes from a pipe
                   '-vcodec', 'libx264',
                   '-b:v', self.bitrate,
                   fileName]

        pipe = sp.Popen(cmd_out, stdin=sp.PIPE)

        bs = timeit.default_timer()

        while self.running:
            s = timeit.default_timer()

            try:
                img = Capture.getCaptureImage(int(self.hwndref[0]))
            except Exception as e:
                break

            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

            img = np.require(img, dtype=np.uint8, requirements=['C'])
            if img.shape[1] < width/height*img.shape[0]:

                larray = np.zeros(
                    (img.shape[0], int((width/height*img.shape[0] - img.shape[1])/2), 3), dtype='uint8')

                img = np.concatenate((larray, img, larray), axis=1)

            elif img.shape[0] < img.shape[1] * height / width:
                larray = np.zeros(
                    (int((img.shape[1] * height / width - img.shape[0]) / 2), img.shape[1], 3), dtype='uint8')

                img = np.concatenate((larray, img, larray), axis=0)

            img = cv2.resize(
                img, (width, height))

            if self.paused == False:
                # cv2.imshow('Original', img)
                # cv2.waitKey(1)

                # out.write(img)
                img = Image.fromarray(img)
                img.save(pipe.stdin, "JPEG")

            i += 1

            left = (1/FPS) - (timeit.default_timer() - s)

            if left > 0:
                time.sleep(left)

            # time.sleep(1)

            # print(left)

        # print(f"recording timing {timeit.default_timer() - bs}")
        # out.release()
        # converting

        # pipe solution
        pipe.stdin.close()
        pipe.wait()
        # pipe solution

        # try:
        #     if os.path.exists(fileName):
        #         outName = f"{path}/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f') }.mp4"
        #         stream = ffmpeg.input(fileName)
        #         stream = ffmpeg.output(
        #             stream, outName, **{'c:v': 'libx264', 'b:v': self.bitrate})
        #         ffmpeg.run(stream, quiet=False)
        #         os.remove(fileName)
        #     else:
        #         print("The file does not exist")

        # except Exception as e:
        #     print(e)
        #     pass

        self.finishedSingnl.emit()
