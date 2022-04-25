import sys
from overlay import App
from getScreen import Capture
import timeit
import numpy as np
import os
import cv2
import win32api
import win32gui
import win32ui
import win32con
import numpy as np
import time
from PyQt5.QtCore import QThread, pyqtSignal

yolos = [
    'YOLOv3-320',
    'yolov3-608',
    'yolov3-tiny'
]


Confidencethreshold = 0.3
overlapThreshold = 0.2
inWH = int(320)

yolo = yolos[1]
DIR = "models"


# get visiable window handlers

if __name__ == "__main__":
    print('prohibited..')
    exit()


class ObjectDetectionThread(QThread):
    finshed = pyqtSignal()

    def __init__(self, hwnd: int) -> None:

        super().__init__()

        self.running = True

        self.windowHandler = hwnd

    def run(self) -> None:

        labelsFile = f"{DIR}\coco-dataset.labels"
        cfgFile = f"{DIR}\{yolo}.cfg"
        weightsFile = f"{DIR}\{yolo}.weights"

        # Test for GPU support
        build_info = str("".join(cv2.getBuildInformation().split()))
        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)
            cv2.ocl.useOpenCL()
            print("[OKAY] OpenCL is working!")
        else:
            print(
                "[WARNING] OpenCL acceleration is disabled!")

        if "CUDA:YES" in build_info:
            print("[OKAY] CUDA is working!")

        else:
            print(
                "[WARNING] CUDA acceleration is disabled!")
        print()

        # read nurale network
        net = cv2.dnn.readNetFromDarknet(cfgFile, weightsFile)

        # configarations
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)

        # all laers names
        layerNames = net.getLayerNames()

        # outputlayers (not string)

        # get names of the outputlayers
        layerNames = [layerNames[i - 1]
                      for i in net.getUnconnectedOutLayers()]

        # image to dettect
        # img = cv2.imread('image.png')
        # conver image into blob
        # os.system("clear")

        print('[CREATE] Overlay..')
        app = App()
        app.Run()
        print('[OK] Overlay Running..')
        print()
        print()

        while self.running == True:

            try:
                start_time = timeit.default_timer()

                if Capture.isWindowMinimized(self.windowHandler):
                    app.ClearBuffers()
                    time.sleep(1)
                    continue

                img = Capture.getCaptureImage(self.windowHandler)
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                blod = cv2.dnn.blobFromImage(
                    img, 0.01, (inWH, inWH), (0, 0, 0), swapRB=True)

                # network input
                net.setInput(blod)

                # return 3 2d arrays contains cofidences
                # most slowest part : (
                layerOutputs = net.forward(layerNames)

                #

                box = []
                confidence = []

                for output in layerOutputs:
                    # mask to select over confidencethreshold
                    mask = (output[:, 5] > Confidencethreshold)
                    # extract over confidencethreshold
                    # bounding boxes
                    bb = output[mask, :]

                    if len(bb) > 0:
                        for i in bb:
                            # append extracted bounding boxes to bb list
                            box.append(i[:4])
                            confidence.append(i[5])

                # convert np.array box to list
                boxarray = [i.tolist() for i in box]

                # overlap suppresion
                boxindexes = cv2.dnn.NMSBoxes(boxarray, confidence,
                                              Confidencethreshold, overlapThreshold)

                # boxarray after suppresion
                boxarray = [boxarray[i] for i in boxindexes]
                confidence = [confidence[i] for i in boxindexes]

                # images demenssions
                H, W = img.shape[: 2]

                # transform box coordinats and size to image scale
                if len(boxarray) > 0:
                    boxarray = boxarray * np.array([W, H, W, H])

                app.ClearBuffers()

                i = 0
                left, top, right, bot = 0, 0, 0, 0

                if self.windowHandler == 0:
                    left, top, right, bot = win32gui.GetWindowRect(
                        win32gui.GetDesktopWindow())
                else:
                    left, top, right, bot = win32gui.GetWindowRect(
                        self.windowHandler)

                for box in boxarray:
                    # translate x, y
                    x = int(box[0] - box[2]/2)
                    y = int(box[1] - box[3]/2)
                    w = int(box[2])
                    h = int(box[3])

                    text = f"TARGET {int(confidence[i] * 100)}%"

                    if Capture.isWindowMinimized(self.windowHandler) == False:
                        app.appendBoxsStream([x + left, y + top, w, h, 3])
                        app.appendTextStream([x + left, y + top, text])
                    else:
                        app.ClearBuffers()

                    i += 1

                    # cv2.circle(img, (x, y),
                    #            5, (0, 0, 255), -1)
                    # cv2.rectangle(img, (x, y),
                    #               (x + w, y + h), (0, 0, 255), 2)
                elapsed = timeit.default_timer() - start_time

                text2 = f"TARGET COUNT: {len(boxarray)}"
                fpsText = f"FPS: {'%.2f' % float(1/elapsed)}"

                app.appendTextStream([20, 40, text2])
                app.appendTextStream([20, 70, fpsText])

                sys.stdout.write(
                    f"\rFPS: { '%.2f' % float(1/elapsed)} delay: {int((elapsed)*1000)} ms"+" "*10
                )

                # if Capture.isWindowMinimized(self.windowHandler) == False:
                #     cv2.imshow("window", img)
                #     cv2.waitKey(1)
                #     pass
                # else:
                #     cv2.destroyAllWindows()
                #     pass
                del img
                del layerOutputs
            except Exception as identifier:
                self.running = False

        del net

        app.ClearBuffers()

        app.terminate()
        os.system("clear")

        self.finshed.emit()
