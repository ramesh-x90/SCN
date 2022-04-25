
import threading
import cv2
import win32gui
import win32ui
import win32con
import win32api
import numpy as np
from ctypes import windll
from PIL import Image

# name = "Google Chrome"
# l = []


# def winEnumHandler(hdw, ctx):
#     if win32gui.IsWindowVisible(hdw):

#         print(hex(hdw), win32gui.GetWindowText(hdw))

#         if name in str(win32gui.GetWindowText(hdw)):
#             l.append(hdw)


# win32gui.EnumWindows(winEnumHandler, None)


# window_handler = l[0]
# win32gui.SetForegroundWindow(window_handler)


# win32gui.BringWindowToTop(window_handler)
# GetWindowDC() for entir window


if __name__ == "__main__":
    print("This is a module import it to use it")
    exit()


class Capture:
    lock = threading.Lock()

    def getCaptureImage(window_handler: int):
        Capture.lock.acquire()
        try:
            # hwin = win32gui.GetDesktopWindow()
            HDC = win32gui.GetWindowDC(window_handler)

            mfcDC = win32ui.CreateDCFromHandle(HDC)

            saveDC = mfcDC.CreateCompatibleDC()

            left, top, right, bot = 0, 0, 0, 0

            if window_handler == 0:
                left, top, right, bot = win32gui.GetWindowRect(
                    win32gui.GetDesktopWindow())
            else:
                left, top, right, bot = win32gui.GetWindowRect(window_handler)
            w = right - left
            h = bot - top

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

            saveDC.SelectObject(saveBitMap)

            result = saveDC.BitBlt((0, 0), (w, h), mfcDC,
                                   (0, 0), win32con.SRCCOPY)

            # result = windll.user32.PrintWindow(
            #     window_handler, saveDC.GetSafeHdc(), 1)

            if result == 0:
                return 0

            # bmpinfo = saveBitMap.GetInfo()
            # bmpstr = saveBitMap.GetBitmapBits(True)

            # img = Image.frombuffer(
            #     'RGB',
            #     (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            #     bmpstr, 'raw', 'BGRX', 0, 1)

            signedIntsArray = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(signedIntsArray, dtype='uint8')

            img.shape = (h, w, 4)

            # win32gui.DeleteObject(saveBitMap.GetHandle())
            # saveDC.DeleteDC()
            # mfcDC.DeleteDC()
            # win32gui.ReleaseDC(window_handler, HDC)

            def release():
                if saveBitMap != None:
                    win32gui.DeleteObject(saveBitMap.GetHandle())

                if saveDC != None:
                    saveDC.DeleteDC()
                if mfcDC != None:
                    mfcDC.DeleteDC()
                if window_handler != None or HDC != None:
                    win32gui.ReleaseDC(window_handler, HDC)

            release()
            Capture.lock.release()
            return img
        except Exception as e:
            Capture.lock.release()
            raise Exception(e)

    def isWindowMinimized(wnhl: list) -> bool:

        if wnhl == 0:
            id = win32gui.GetDesktopWindow()
        else:
            id = wnhl

        tup = win32gui.GetWindowPlacement(id)

        if tup[1] == win32con.SW_SHOWMINIMIZED:
            return True

        return False
