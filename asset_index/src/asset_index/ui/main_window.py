from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from asset_index.core import library_index
from asset_index.ui import global_lib_pane, local_lib_pane, import_lib_pane
from asset_index.utils import import_utils


class AssetIndex(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(AssetIndex, self).__init__(parent=parent)

        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))
        self.core_index = library_index.LibraryIndex()

        self.resize(1500, 900)
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.central_layout.addLayout(self.button_layout)

        self.stack = QtWidgets.QStackedWidget()
        self.central_layout.addWidget(self.stack)


        self.global_lib = QtWidgets.QPushButton("Global Library")
        self.local_lib = QtWidgets.QPushButton("Local Library")
        self.import_library = QtWidgets.QPushButton("Import Library")

        self.import_library_frame = import_lib_pane.ImportLibrary(self.core_index)
        self.global_lib_frame = global_lib_pane.GlobalLib(self.core_index)
        self.local_lib_frame = local_lib_pane.LocalLib(self.core_index)

        _widgets = [[self.global_lib, self.global_lib_frame],
                    [self.local_lib, self.local_lib_frame],
                    [self.import_library, self.import_library_frame], ]

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
