from importlib import reload
from pathlib import Path

from PySide6 import QtWidgets, QtGui

from asset_index.asset_import import base_import_kit
from asset_index.structure import structure_resolver

reload(structure_resolver)


class ImportLibrary(QtWidgets.QFrame):
    def __init__(self, core_index, parent=None):
        super(ImportLibrary, self).__init__(parent=parent)
        self.core_index = core_index
        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.central_layout.addWidget(self.splitter)

        self.libraries_view = QtWidgets.QTreeWidget()
        self.splitter.addWidget(self.libraries_view)
        self.libraries_view.setHeaderLabel("Libraries")
        self.populate_libraries_view(self.core_index.global_asset_lib, self.libraries_view)

        self.library_data = QtWidgets.QWidget()
        self.splitter.addWidget(self.library_data)

        self.library_data_layout = QtWidgets.QVBoxLayout()
        self.library_data.setLayout(self.library_data_layout)
        self.splitter.setSizes([150, 450])

        self.buttons_group = QtWidgets.QFrame()
        self.library_data_layout.addWidget(self.buttons_group)
        self.buttons_group_layout = QtWidgets.QHBoxLayout()
        self.buttons_group.setLayout(self.buttons_group_layout)

        self.validate_lib = QtWidgets.QPushButton("Validate")
        self.buttons_group_layout.addWidget(self.validate_lib)

        self.edit_lib = QtWidgets.QPushButton("Edit")
        self.buttons_group_layout.addWidget(self.edit_lib)

        self.import_lib = QtWidgets.QPushButton("Import")
        self.buttons_group_layout.addWidget(self.import_lib)

        self.validate_lib.clicked.connect(self.validate)
        self.import_lib.clicked.connect(self.import_library)

    def populate_libraries_view(self, root: Path, parent_item):
        folders = sorted((p for p in root.iterdir() if not p.name.startswith(".")),
                         key=lambda p: p.name.lower())
        for folder in folders:
            if not folder.is_dir() and not "usd" in folder.suffix:
                continue
            item = QtWidgets.QTreeWidgetItem(parent_item)
            item.setText(0, folder.name)
            if folder.is_dir():
                self.populate_libraries_view(folder, item)

    def get_selected_library(self):
        """
        Returns the currently selected item.
        If nothing is selected, returns the invisible root item.
        """
        selected = self.libraries_view.selectedItems()
        return selected[0] if selected else None

    def validate(self):
        selected_library = self.get_selected_library()
        if not selected_library:
            QtWidgets.QMessageBox.information(
                self,
                "No Library Selected",
                "Please select a library root folder before running validation"
            )
            return

        st = structure_resolver.LibraryStructureResolver(selected_library.text(0))
        st.run_library_validation()

    def import_library(self):
        selected = self.get_selected_library().text(0)
        lib_path = self.core_index.global_asset_lib / selected
        import_lib = base_import_kit.BaseKitImporter(str(lib_path))
        import_lib.import_library()
