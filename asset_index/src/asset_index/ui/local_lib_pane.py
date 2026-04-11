from PySide6 import QtWidgets, QtGui


class LocalLib(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(LocalLib, self).__init__(parent=parent)
        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)

