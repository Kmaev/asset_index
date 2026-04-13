from importlib import reload
from pathlib import Path

from PySide6 import QtWidgets, QtGui, QtCore

from asset_index.asset_import import qt_import_kit
from asset_index.structure import structure_resolver

reload(structure_resolver)


class ImportLibrary(QtWidgets.QFrame):
    """UI widget for validating and importing asset libraries."""

    update_global_lib = QtCore.Signal()

    def __init__(self, core_index, parent=None):
        super(ImportLibrary, self).__init__(parent=parent)
        self.library_path = None
        self.library = None
        self.core_index = core_index

        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.central_layout.addWidget(self.splitter)

        self.libraries_view = QtWidgets.QTreeWidget()
        self.splitter.addWidget(self.libraries_view)
        self.libraries_view.setHeaderLabel("Library Content")

        self.library_data = QtWidgets.QWidget()
        self.splitter.addWidget(self.library_data)

        self.library_data_layout = QtWidgets.QVBoxLayout()
        self.library_data.setLayout(self.library_data_layout)
        self.splitter.setSizes([200, 400])

        self.buttons_group = QtWidgets.QFrame()
        self.library_data_layout.addWidget(self.buttons_group)
        self.buttons_group_layout = QtWidgets.QHBoxLayout()
        self.buttons_group_layout.setAlignment(QtCore.Qt.AlignTop)
        self.buttons_group.setLayout(self.buttons_group_layout)

        self.validate_lib = QtWidgets.QPushButton("Validate")
        self.buttons_group_layout.addWidget(self.validate_lib)

        self.edit_lib = QtWidgets.QPushButton("Edit")
        self.buttons_group_layout.addWidget(self.edit_lib)
        self.edit_lib.setDisabled(True)

        self.import_lib = QtWidgets.QPushButton("Import")
        self.buttons_group_layout.addWidget(self.import_lib)
        self.import_lib.setDisabled(True)

        self.validate_lib.clicked.connect(self.validate)
        self.import_lib.clicked.connect(self.import_library)
        self.validation_passed = False

        self.libraries_view.itemSelectionChanged.connect(self.trigger_validation)

    def populate_libraries_view(self, root: Path, parent_item):
        """Populate tree view with library content."""
        folders = sorted((p for p in root.iterdir() if not p.name.startswith(".")),
                         key=lambda p: p.name.lower())
        for folder in folders:
            if not folder.is_dir() and not "usd" in folder.suffix:
                continue
            item = QtWidgets.QTreeWidgetItem(parent_item)
            item.setText(0, folder.name)
            if folder.is_dir():
                self.populate_libraries_view(folder, item)

    def validate(self):
        """Validate selected library folder structure."""
        st = structure_resolver.LibraryStructureResolver(self.library)
        self.validation_passed = all(st.run_library_validation())
        if self.validation_passed:
            self.enable_import_button()
        else:
            self.enable_edit_button()

    def trigger_validation(self):
        """Reset validation state on library selection change."""
        self.import_lib.setDisabled(True)
        self.edit_lib.setDisabled(True)
        self.validation_passed = False

    def enable_import_button(self):
        """Enable import action."""
        self.import_lib.setDisabled(False)

    def enable_edit_button(self):
        """Enable edit action."""
        self.edit_lib.setDisabled(False)

    def import_library(self):
        """Run library import process."""
        import_lib = qt_import_kit.QtKitImporter(str(self.library_path))
        import_lib.import_library()

        if not import_lib.completed:
            self.trigger_validation()
            return

        self.update_global_lib.emit()
        self.libraries_view.clear()

    def set_library(self, library: str):
        """Set currently selected library and populate view."""
        self.libraries_view.clear()
        self.library = library
        self.library_path = self.core_index.global_asset_lib / self.library
        self.populate_libraries_view(self.library_path, self.libraries_view)
        self.trigger_validation()
