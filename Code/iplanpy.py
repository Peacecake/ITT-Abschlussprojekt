import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui


class IPlanPy(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        print("load_ui")
        self.ui = uic.loadUi("iplanpy.ui", self)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    i_plan_py = IPlanPy()
    sys.exit(app.exec_())
