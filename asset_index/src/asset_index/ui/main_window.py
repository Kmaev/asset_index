from PySide6 import QtCore, QtGui, QtWidgets

from asset_index.ui import global_lib_pane, local_lib_pane, import_lib_pane


class AssetIndex(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(AssetIndex, self).__init__(parent=parent)
        self.resize(1500, 900)
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.central_layout.addLayout(self.button_layout)

        self.stack = QtWidgets.QStackedWidget()
        self.central_layout.addWidget(self.stack)

        self.import_assets = QtWidgets.QPushButton("Import Assets")
        self.global_lib = QtWidgets.QPushButton("Global Library")
        self.local_lib = QtWidgets.QPushButton("Local Library")

        self.import_assets_frame = import_lib_pane.ImportLibrary()
        self.global_lib_frame = global_lib_pane.GlobalLib()
        self.local_lib_frame = local_lib_pane.LocalLib()

        _widgets = [[self.global_lib, self.global_lib_frame],
                    [self.local_lib, self.local_lib_frame],
                    [self.import_assets, self.import_assets_frame], ]

        for i, (button, frame) in enumerate(_widgets):
            self.button_layout.addWidget(button)
            self.stack.addWidget(frame)
            button.setProperty('stack-index', i)

            button.clicked.connect(self.on_button_clicked)

    def on_button_clicked(self):
        button = self.sender()

        index = button.property('stack-index')
        self.stack.setCurrentIndex(index)


def main():
    app = QtWidgets.QApplication([])
    win = AssetIndex()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
