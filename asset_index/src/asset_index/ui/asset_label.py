from PySide6 import QtWidgets, QtCore, QtGui


class AssetFrame(QtWidgets.QFrame):

    def __init__(self, asset_path, parent=None):
        super(AssetFrame, self).__init__(parent=parent)
        self.asset_path = asset_path

        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)
        self.central_layout.setContentsMargins(2, 2, 2, 2)
        self.central_layout.setSpacing(0)

        path = str(self.asset_path.with_suffix(".png"))
        pixmap = QtGui.QPixmap(path)
        size = QtCore.QSize(200, 200)
        pixmap = pixmap.scaled(size, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
        rect = QtCore.QRect((pixmap.width() - size.width()) // 2, (pixmap.height() - size.height()) // 2, size.width(),
                            size.height())

        pixmap = pixmap.copy(rect)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setMaximumSize(size)
        self.image_label.setMinimumSize(size)

        self.central_layout.addWidget(self.image_label)
        self.image_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.label = QtWidgets.QLabel()
        self.label = QtWidgets.QLabel()
        self.label.setMaximumSize(size)
        self.label.setText(self.asset_path.stem)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.central_layout.addWidget(self.label)
        self.image_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
