from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from asset_index.core import library_index
from asset_index.ui import global_lib_pane, local_lib_pane
from asset_index.utils import import_utils


class AssetIndex(QtWidgets.QMainWindow):
    """Main window for asset library UI."""

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

        #Add Global and Local Library Buttons
        self.global_lib = QtWidgets.QPushButton("Global Library")
        self.local_lib = QtWidgets.QPushButton("Local Library")

        self.global_lib_frame = global_lib_pane.GlobalLib(self.core_index)
        self.global_lib_frame.load_asset_request.connect(self.load_asset)

        self.local_lib_frame = local_lib_pane.LocalLib(self.core_index)

        _widgets = [[self.global_lib, self.global_lib_frame],
                    [self.local_lib, self.local_lib_frame]]
        for i, (button, frame) in enumerate(_widgets):
            self.button_layout.addWidget(button)
            self.stack.addWidget(frame)
            button.setProperty('stack-index', i)

            button.clicked.connect(self.on_button_clicked)

        # Add Import Library Button
        self.import_library = QtWidgets.QPushButton("Import Library")
        self.button_layout.addWidget(self.import_library)
        self.import_library.clicked.connect(self.global_lib_frame.on_start_import_clicked)
        self.import_library.clicked.connect(self.global_lib_frame.on_start_import_clicked)

        style_file = Path(__file__).resolve().parents[3] / "resources" / "style.qss"
        style = ""

        if style_file.is_file():
            with open(style_file, 'r') as f:
                style = f.read()
        self.setStyleSheet(style)

        if self.parent():
            self.parent().setStyleSheet(self.parent().styleSheet())

    def on_button_clicked(self):
        """Switch stacked view based on clicked button."""
        button = self.sender()

        index = button.property('stack-index')
        self.stack.setCurrentIndex(index)

    def load_asset(self, asset_path):
        """Each DCC should implement asset loading functionality according to its requirements."""
        pass


app_win = None


def show(parent=None):
    global app_win
    app_win = AssetIndex(parent=parent)
    app_win.show()
    return app_win


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = AssetIndex()
    win.show()
    app.exec_()
