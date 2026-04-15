from PySide6 import QtWidgets, QtCore, QtGui

from asset_index import config
class AssetFrame(QtWidgets.QFrame):
    """UI widget displaying an asset thumbnail and name."""

    def __init__(self, asset_path, parent=None):
        super(AssetFrame, self).__init__(parent=parent)
        self.render_config = config.RenderConfig()
        self.asset_path = asset_path

        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)
        self.central_layout.setContentsMargins(2, 2, 2, 2)
        self.central_layout.setSpacing(0)

        path = str(self.asset_path.with_suffix(f".{self.render_config.image.extension}"))
        pixmap = QtGui.QPixmap(path)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.central_layout.addWidget(self.image_label)
        self.image_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.label = QtWidgets.QLabel()
        self.label = QtWidgets.QLabel()

        self.label.setText(self.asset_path.stem)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.central_layout.addWidget(self.label)
        self.image_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
