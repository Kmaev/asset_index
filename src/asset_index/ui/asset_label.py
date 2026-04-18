from PySide6 import QtWidgets, QtCore, QtGui


class AssetFrame(QtWidgets.QFrame):
    """UI widget displaying an asset thumbnail and name."""

    load_asset_request = QtCore.Signal(object)

    def __init__(self, asset_path, ext, parent=None):
        super(AssetFrame, self).__init__(parent=parent)
        self.asset_path = asset_path
        self.extension = ext

        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)
        self.setFixedSize(200, 200)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.label_widget = QtWidgets.QWidget()
        self.label_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.central_layout.addWidget(self.label_widget)

        self.label_layout = QtWidgets.QVBoxLayout()
        self.label_layout.setContentsMargins(0, 0, 0, 0)
        self.label_widget.setLayout(self.label_layout)
        self.label_layout.setAlignment(QtCore.Qt.AlignCenter)

        path = str(self.asset_path.with_suffix(self.extension))
        pixmap = QtGui.QPixmap(path)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.label_layout.addWidget(self.image_label)

        self.functions = QtWidgets.QFrame()
        self.label_layout.addWidget(self.functions)

        self.functions_layout = QtWidgets.QHBoxLayout()
        self.functions_layout.setAlignment(QtCore.Qt.AlignTop)
        self.functions_layout.setContentsMargins(0, 0, 0, 0)
        self.functions.setLayout(self.functions_layout)

        self.load = QtWidgets.QPushButton("▼")
        self.load.setFixedSize(30, 20)
        self.functions_layout.addWidget(self.load)
        self.load.setObjectName("asset_button")

        self.label = QtWidgets.QLabel()

        self.label.setText(self.asset_path.stem)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("asset_label_text")

        self.central_layout.addWidget(self.label)
        self.image_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.load.clicked.connect(self.on_asset_load_clicked)

    def on_asset_load_clicked(self):
        """Emits assed loaded signal passing the asset path to the main window"""
        self.load_asset_request.emit(self.asset_path)
