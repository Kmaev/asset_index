import json
from importlib import reload
from pathlib import Path

from PySide6 import QtWidgets, QtGui, QtCore

from asset_index.ui import asset_label
from asset_index.utils import import_utils

reload(asset_label)


class GlobalLib(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(GlobalLib, self).__init__(parent=parent)
        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))
        self.libraries_data_file = self.global_asset_lib / "libraries.json"

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
        self.library_not_imported.setText("No assets found. Import a library to get started.")
        self.library_not_imported.setAlignment(QtCore.Qt.AlignCenter)
        self.assets_stack.addWidget(self.library_not_imported)

        self.splitter.setSizes([150, 450])

        self.populate_asset_labels()

        self.libraries.itemSelectionChanged.connect(self.populate_asset_labels)

    def get_selection(self, widget):
        return widget.selectedItems()[0]

    def populate_libraries_list(self):
        with open(self.libraries_data_file, "r") as f:
            libraries_list = json.load(f)
        imported_libraries = sorted([x for x in libraries_list.keys()])
        all_libraries = self.find_all_libraries()
        print("All libraries: ", all_libraries)
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

    def find_all_libraries(self):
        all_libraries = sorted([folder.name for folder in self.global_asset_lib.iterdir() if
                                folder.is_dir()])
        return all_libraries


    def populate_asset_labels(self):
        selected = self.get_selection(self.libraries).text()
        self.current_lib_path = self.global_asset_lib / f"{selected}/library_catalog.json"
        if not self.current_lib_path.is_file():
            self.assets_stack.setCurrentIndex(1)
            return

        self.assets_stack.setCurrentIndex(0)

        self.assets.clear()
        with open(self.current_lib_path, "r") as f:
            self.selected_catalog = json.load(f)

        for path in self.selected_catalog[selected]:
            item = QtWidgets.QListWidgetItem()
            widget = asset_label.AssetFrame(Path(path))
            item.setSizeHint(widget.sizeHint())  # important
            self.assets.addItem(item)
            self.assets.setItemWidget(item, widget)
