from importlib import reload
from pathlib import Path

from PySide6 import QtWidgets, QtGui, QtCore

from asset_index.ui import asset_label

reload(asset_label)


class GlobalLib(QtWidgets.QFrame):
    def __init__(self, core_index, parent=None):
        super(GlobalLib, self).__init__(parent=parent)

        self.core_index = core_index
        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.central_layout.addWidget(self.splitter)

        self.libraries = QtWidgets.QListWidget()
        self.populate_libraries_list()
        self.libraries.setCurrentRow(0)
        self.splitter.addWidget(self.libraries)

        self.assets_stack = QtWidgets.QStackedWidget()
        self.splitter.addWidget(self.assets_stack)

        self.assets = QtWidgets.QListWidget()
        self.assets.setViewMode(QtWidgets.QListView.IconMode)
        self.assets.setResizeMode(QtWidgets.QListView.Adjust)
        self.assets.setWrapping(True)
        self.assets.setFlow(QtWidgets.QListView.LeftToRight)
        self.assets.setSpacing(10)
        self.assets.setIconSize(QtCore.QSize(150, 150))

        self.assets.setMovement(QtWidgets.QListView.Static)
        self.assets.setUniformItemSizes(True)
        self.assets_stack.addWidget(self.assets)

        self.library_not_imported = QtWidgets.QLineEdit()
        self.library_not_imported.setText("No assets found. Import the library to get started.")
        self.library_not_imported.setAlignment(QtCore.Qt.AlignCenter)
        self.assets_stack.addWidget(self.library_not_imported)

        self.splitter.setSizes([150, 450])

        self.populate_asset_labels()

        self.libraries.itemSelectionChanged.connect(self.populate_asset_labels)

    def get_selection(self, widget):
        return widget.selectedItems()[0]

    def populate_libraries_list(self):

        imported_libraries = self.core_index.list_imported_libraries()
        all_libraries = self.core_index.list_all_libraries()

        for lib in imported_libraries:
            self._add_library_item(lib, self.libraries, imported=True)
        for lib in all_libraries:
            if lib not in imported_libraries:
                self._add_library_item(lib, self.libraries, imported=False)

    def _add_library_item(self, name, parent, imported=True):
        item = QtWidgets.QListWidgetItem(parent)
        item.setText(name)
        metadata = {"imported": imported}
        item.setData(QtCore.Qt.UserRole, metadata)

    def populate_asset_labels(self):
        selected = self.get_selection(self.libraries).text()
        selected_catalog = self.core_index.load_library_catalog(selected)

        if not selected_catalog:
            self.assets_stack.setCurrentIndex(1)
            return

        self.assets_stack.setCurrentIndex(0)

        self.assets.clear()

        for path in selected_catalog:
            item = QtWidgets.QListWidgetItem()
            widget = asset_label.AssetFrame(Path(path))
            item.setSizeHint(widget.sizeHint())
            self.assets.addItem(item)
            self.assets.setItemWidget(item, widget)
