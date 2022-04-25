

import math
from threading import Thread, Lock
import threading
import time
import glfw
import win32api
import win32gui
import win32con

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


if __name__ == "__main__":
    print("This is a module import it to use it")
    exit()


class overlay:
    def __init__(self):
        glfw.init()
        glutInit()
        self.window, self.videoMode = self.create_window()

    def create_window(self):
        glfw.window_hint(glfw.DECORATED, 0)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, 1)
        glfw.window_hint(glfw.FLOATING, 1)
        glfw.window_hint(glfw.SAMPLES, 14)

        # get display width and height
        v_mode = glfw.get_video_mode(glfw.get_primary_monitor())
        window_width = v_mode.size.width - 1
        window_hight = v_mode.size.height - 2

        # create window
        window = glfw.create_window(
            window_width, window_hight, "window", None, None)
        glfw.make_context_current(window)

        # make window overlayed

        hwnd = glfw.get_win32_window(window)
        # make window translution for inputs
        win32gui.SetWindowLong(
            hwnd, win32con.GWL_EXSTYLE,
            win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        )
        # win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0,
        #                       0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        glInitGl46VERSION()
        glOrtho(0 - 2, window_width, window_hight, 0 - 7,  -1, 1)

        return window, v_mode

    def isAlive(self):
        return not glfw.window_should_close(self.window)

    def update(self):
        glfw.swap_buffers(self.window)
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT)

    def drawBox(self, x, y, width, height, line_width, color=(255, 0, 0)):
        Draw.outline(x, y, width, height, line_width, color)

    def drawText(self, x, y,  text, color=(255, 0, 0)):
        Draw.text(x, (-1)*y + self.videoMode.size.height, color, text)

    def show(self):
        self.update()

    def destroy(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glfw.terminate()


class Draw:
    red = (250, 0, 0)
    green = (0, 250, 0)
    blue = (0, 0, 250)
    black = (0, 0, 0)
    white = (250, 250, 250)

    @staticmethod
    def line(x1, y1, x2, y2, line_width, color=None):
        glLineWidth(line_width)
        glBegin(GL_LINES)
        glColor3f(*color)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    @staticmethod
    def outline(x, y, width, height, line_width, color):
        glLineWidth(line_width)
        glBegin(GL_LINE_LOOP)
        glColor3f(*color)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    @staticmethod
    def text(x, y, color, text, font=GLUT_BITMAP_9_BY_15):
        glColor3f(*color)
        glWindowPos2f(x, y)
        [glutBitmapCharacter(font, ord(ch)) for ch in text]


class Gl_Thread(threading.Thread):
    def __init__(self, box_input_, text_, lock: Lock):
        self.box_input_stream = box_input_
        self.text_stream = text_
        self.stop_flag: bool = False
        self.lock = lock
        super().__init__()

    def run(self):
        fps: float = 1/10
        OverLay = overlay()
        while OverLay.isAlive():

            self.lock.acquire()

            if len(self.box_input_stream) != 0:
                for box in self.box_input_stream:
                    OverLay.drawBox(*box)

            if len(self.text_stream) != 0:
                for texts in self.text_stream:
                    OverLay.drawText(*texts)

            self.lock.release()

            time.sleep(fps)
            OverLay.update()

            if self.stop_flag == 1:
                break

        OverLay.destroy()


class App:

    def __init__(self) -> None:
        self.runing = True

        # buffer to reder resources
        self.b_buffer: list = []
        self.t_buffer: list = []
        self.lock = Lock()
        # rederig thread
        self.t = Gl_Thread(self.b_buffer, self.t_buffer, self.lock)

    def Run(self):
        self.t.start()

    def terminate(self):
        self.runing = False
        if self.t.is_alive():
            print('thread stil runing')
            self.t.stop_flag = True
        self.t.join()

    def appendBoxsStream(self, data: list):
        self.b_buffer.append(data)

    def appendTextStream(self, data: list):
        self.lock.acquire()
        self.t_buffer.append(data)
        self.lock.release()

    def ClearBuffers(self):
        self.lock.acquire()
        self.b_buffer.clear()
        self.t_buffer.clear()
        self.lock.release()
