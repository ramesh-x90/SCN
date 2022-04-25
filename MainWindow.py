from recorder import reCorder
import sys
from OBJR import ObjectDetectionThread
import threading
from PyQt5.QtCore import QTimer, Qt
from PyQt5.uic import loadUi
from getScreen import Capture
from PyQt5.QtGui import QImage, QPixmap,  QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QRadioButton,  QSizeGrip
import numpy as np
import cv2
import win32gui


PREVIEWFPS: int = 10
FPS = 15

lock = threading.Lock()


class Window(QMainWindow):

    windowlist = []

    windowHandler = [0]

    recording = False
    recordingPaused = False

    def __init__(self, name: int) -> None:
        super().__init__()

        self.showPreview = True

        loadUi('app.ui', self)

        self.setWindowTitle(name)

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.titleBar.mouseMoveEvent = moveWindow

        self.grip = QSizeGrip(self.resizegrip)
        self.grip.setToolTip("Resize Window")

        self.grip2 = QSizeGrip(self.resizegrip2)
        self.grip2.setToolTip("Resize Window")

        self.setWindowIcon(QIcon('asset/logo.png'))

        self.RefreshBtn.clicked.connect(self.refreshWIndowList)

        self.RecordBtn.clicked.connect(self.workerStartRecord)

        self.PauseBtn.clicked.connect(self.workerPauseRecord)

        self.Exit.clicked.connect(self.Exitfunc)
        self.minimiz.clicked.connect(lambda: self.showMinimized())

        self.refreshWIndowList()

        def setWindowHandler():
            Window.windowHandler[0] = int(Window.windowlist[self.WindowList.currentIndex(
            )][0])

        (self.PreviewCheck).setChecked(True)
        (self.PreviewCheck).stateChanged.connect(self.setPreview)

        # combobox
        self.WindowList.activated.connect(setWindowHandler)

        # detection readio
        self.radioButton1.clicked.connect(self.ObjDetectionWorker)

        self.timer = QTimer(self)
        # Add a method with the timer
        self.timer.timeout.connect(self.upDatePreview)
        # Call start() method to modify the timer value
        self.timer.start(1000//PREVIEWFPS)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def ObjDetectionWorker(self):

        if self.radioButton1.isChecked():
            self.objThread = ObjectDetectionThread(Window.windowHandler[0])
            self.objThread.finished.connect(
                lambda: {self.radioButton1.setEnabled(True), self.radioButton1.setChecked(False)})
            self.objThread.start()
        else:

            if self.objThread != None and self.objThread.isRunning():
                self.radioButton1.setEnabled(False)
                self.objThread.running = False
                del self.objThread

    def setPreview(self):

        if (self.PreviewCheck). isChecked() == True:
            self.showPreview = True
        else:
            self.qimage.clear()
            self.showPreview = False

    @ staticmethod
    def winEnumHandler(hdw, ctx):
        if win32gui.IsWindowVisible(hdw):
            Window.windowlist.append([hdw, win32gui.GetWindowText(hdw)])

    def refreshWIndowList(self):
        Window.windowlist.clear()
        Window.windowlist.append([0, "full screen"])
        win32gui.EnumWindows(Window.winEnumHandler, None)

        Window.windowlist = np.array(Window.windowlist)
        Window.windowlist = Window.windowlist[Window.windowlist[:, 1] != '']
        Window.windowlist = Window.windowlist[Window.windowlist[:, 1] != self.windowTitle()].tolist(
        )

        self.WindowList.clear()
        self.WindowList.addItems([item[1] for item in Window.windowlist])
        pass

    def upDatePreview(self):
        if self.showPreview == True:
            try:
                img = Capture.getCaptureImage(int(Window.windowHandler[0]))
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                img = np.require(img, dtype=np.uint8, requirements=['C'])

                imgPreview = cv2.resize(
                    img, (800, 450))

                image = QImage(
                    imgPreview, imgPreview.shape[1], imgPreview.shape[0], QImage.Format_RGB888)

                self.qimage.setPixmap(QPixmap(image))

            except Exception as e:
                self.qimage.clear()
                self.showPreview = False
                mb = QMessageBox()
                mb.setIcon(QMessageBox.Information)
                mb.setText(e.__str__())
                mb.setStandardButtons(QMessageBox.Ok)
                mb.exec_()

    def workerStartRecord(self):
        if self.recording == False:

            Window.recording = True

            self.reThread = reCorder(
                self.resolutions.currentIndex(), Window.windowHandler)
            self.reThread.setBitRtate(self.bitRateCombo.currentIndex())

            # self.reThread.frame.connect(self.func)

            self.reThread.finishedSingnl.connect(self.workerStopRecord)

            self.RecordBtn.setText("stop")
            self.lableNOTIFY.setText('Recording')

            self.reThread.start()

        else:

            self.reThread.running = False
            self.RecordBtn.setEnabled(False)

    def workerPauseRecord(self):

        if Window.recording is False:
            return

        if self.reThread != None and self.reThread.isRunning():

            if Window.recordingPaused is False:

                self.reThread.paused = True
                Window.recordingPaused = True

                self.lableNOTIFY.setText('Paused')
                self.PauseBtn.setText('Resume')
            else:
                self.reThread.paused = False
                Window.recordingPaused = False

                self.lableNOTIFY.setText('Recording')
                self.PauseBtn.setText('Pause')

    def workerStopRecord(self):

        Window.recordingPaused = False
        Window.recording = False

        self.RecordBtn.setText("Record")
        self.lableNOTIFY.setText('')
        self.PauseBtn.setText('Pause')
        self.RecordBtn.setEnabled(True)

    def Exitfunc(self):
        if self.recording:
            msg = QMessageBox()
            msg.setWindowTitle('Can not Exit!')
            msg.setIcon(QMessageBox.Information)
            msg.setText("stop recording to exit")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        else:
            self.close()
