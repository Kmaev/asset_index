from PySide6 import QtWidgets, QtGui


class LocalLib(QtWidgets.QFrame):
    def __init__(self, core_index, parent=None):
        super(LocalLib, self).__init__(parent=parent)
        self.core_index = core_index
        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)
