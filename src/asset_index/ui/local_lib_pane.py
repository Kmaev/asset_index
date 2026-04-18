from PySide6 import QtWidgets, QtGui, QtCore


class LocalLib(QtWidgets.QFrame):
    """Placeholder UI for local library (not implemented)."""

    def __init__(self, core_index, parent=None):
        super(LocalLib, self).__init__(parent=parent)
        self.core_index = core_index
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.central_layout)

        message = "Turn back. You’ve reached the world’s edge. None but devils play past here."

        self.add_message("Not Implemented")
        self.add_message(message)

    def add_message(self, message):
        not_implemented = QtWidgets.QLineEdit()
        not_implemented.setEnabled(False)
        not_implemented.setText(message)
        not_implemented.setAlignment(QtCore.Qt.AlignCenter)
        not_implemented.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.central_layout.addWidget(not_implemented)
