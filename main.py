
import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import Window


app = QApplication(sys.argv)

window = Window('SCN')
window.show()

app.exec_()
app.flush()
