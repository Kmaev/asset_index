from pathlib import Path

from PySide6 import QtWidgets, QtGui

from asset_index.utils import import_utils


class ImportLibrary(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(ImportLibrary, self).__init__(parent=parent)
        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))

        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)

        self.libraries_view = QtWidgets.QTreeWidget()
        self.central_layout.addWidget(self.libraries_view)
        self.libraries_view.setHeaderLabel("Libraries")
        self.populate_libraries_view(self.global_asset_lib, self.libraries_view)

        self.library_data = QtWidgets.QWidget()
        self.central_layout.addWidget(self.library_data)

        self.library_data_layout = QtWidgets.QVBoxLayout()
        self.library_data.setLayout(self.library_data_layout)

    def populate_libraries_view(self, root: Path, parent):
        folders = sorted((p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")),
                         key=lambda p: p.name.lower())

        for folder in folders:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setText(0, folder.name)
            self.populate_libraries_view(folder, item)
