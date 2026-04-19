from pathlib import Path

from PySide6 import QtWidgets, QtGui, QtCore

from asset_index.asset_import import qt_import_kit, editor
from asset_index.core import structure_resolver


class ImportLibrary(QtWidgets.QFrame):
    """UI widget for validating and importing asset libraries."""

    update_global_lib = QtCore.Signal()

    def __init__(self, core_index, parent=None):
        super(ImportLibrary, self).__init__(parent=parent)
        self.library_path = None
        self.library = None
        self.editor = None
        self.core_index = core_index

        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([200, 400])
        self.central_layout.addWidget(self.splitter)

        self.libraries_view = QtWidgets.QTreeWidget()
        self.splitter.addWidget(self.libraries_view)
        self.libraries_view.setHeaderLabel("Library Content")
        self.libraries_view.setMinimumWidth(100)
        self.libraries_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.libraries_view.mousePressEvent = self._tree_mouse_press_event

        self.library_data = QtWidgets.QWidget()
        self.splitter.addWidget(self.library_data)

        self.library_data_layout = QtWidgets.QVBoxLayout()
        self.library_data.setLayout(self.library_data_layout)
        self.library_data_layout.setAlignment(QtCore.Qt.AlignTop)
        self.library_data_layout.addSpacing(10)

        self.buttons_group = QtWidgets.QFrame()
        self.buttons_group.setProperty("section", True)
        self.library_data_layout.addWidget(self.buttons_group)
        self.buttons_group_layout = QtWidgets.QHBoxLayout()
        self.buttons_group_layout.setAlignment(QtCore.Qt.AlignTop)
        self.buttons_group.setLayout(self.buttons_group_layout)

        self.validate_lib = QtWidgets.QPushButton("Validate")
        self.buttons_group_layout.addWidget(self.validate_lib)

        self.import_lib = QtWidgets.QPushButton("Import")
        self.buttons_group_layout.addWidget(self.import_lib)
        self.import_lib.setDisabled(True)

        # Editing Features
        self.edit_label = QtWidgets.QLabel()
        self.edit_label.setText("Editing Features")
        self.edit_label.setAlignment(QtCore.Qt.AlignCenter)
        self.library_data_layout.addWidget(self.edit_label)

        self.edit_group = QtWidgets.QFrame()
        self.setProperty("section", True)
        self.library_data_layout.addWidget(self.edit_group)
        self.edit_layout = QtWidgets.QHBoxLayout()
        self.edit_layout.setAlignment(QtCore.Qt.AlignTop)
        self.edit_group.setLayout(self.edit_layout)

        self.create_asset = QtWidgets.QPushButton("Create Asset")
        self.edit_layout.addWidget(self.create_asset)
        self.create_asset.setProperty("edit", True)

        self.group_with_variants = QtWidgets.QPushButton("Group Variants")
        self.edit_layout.addWidget(self.group_with_variants)
        self.group_with_variants.setProperty("edit", True)

        self.validation_passed = False

        self.validate_lib.clicked.connect(self.on_validate_clicked)
        self.import_lib.clicked.connect(self.on_import_clicked)

        self.create_asset.clicked.connect(self.on_create_asset_clicked)
        self.group_with_variants.clicked.connect(self.on_group_variant_clicked)
        self.libraries_view.itemSelectionChanged.connect(self.trigger_validation)

    def set_library(self, library: str):
        """Set currently selected library and trigger populate library content view."""
        self.libraries_view.clear()
        self.library = library
        self.library_path = self.core_index.global_asset_lib / self.library
        self.populate_libraries_view(self.library_path, self.libraries_view)
        self.trigger_validation()

    def populate_libraries_view(self, root: Path, parent_item):
        """Populate tree view with library content."""
        folders = sorted((p for p in root.iterdir() if not p.name.startswith(".")),
                         key=lambda p: p.name.lower())
        for folder in folders:
            if not folder.is_dir() and not "usd" in folder.suffix:
                continue
            item = QtWidgets.QTreeWidgetItem(parent_item)
            item.setText(0, folder.name)
            if "usd" in folder.suffix and folder.is_file():
                metadata = {"usd_file": str(folder)}
                item.setData(0, QtCore.Qt.UserRole, metadata)
            else:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
            if folder.is_dir():
                self.populate_libraries_view(folder, item)

    def _reload_libraries_view(self):
        """Helper to reload the libraries view."""
        self.libraries_view.clear()
        self.populate_libraries_view(self.library_path, self.libraries_view)

    def trigger_validation(self):
        """Reset validation state on library selection change."""
        self.import_lib.setDisabled(True)
        self.validation_passed = False

    def on_validate_clicked(self):
        """Validate selected library folder structure."""
        st = structure_resolver.LibraryStructureResolver(self.core_index, self.library)
        self.validation_passed = all(st.run_library_validation())
        if self.validation_passed:
            QtWidgets.QMessageBox.information(self, "Information", "Assets are ready for import.")
            self.import_lib.setDisabled(False)
        else:
            self._display_warning_message("Validation failed.", "Validation failed. Please fix the asset structure.")

    def enable_import_button(self):
        """Enable import action."""
        self.import_lib.setDisabled(False)

    def on_import_clicked(self):
        """Run library import process."""
        import_lib = qt_import_kit.QtKitImporter(self.core_index, str(self.library))
        import_lib.import_library()

        if not import_lib.completed:
            self.trigger_validation()
            return

        self.update_global_lib.emit()
        self.libraries_view.clear()

    def _tree_mouse_press_event(self, event):
        """Clear selection on empty-space click."""
        item = self.libraries_view.itemAt(event.pos())

        if item is None:
            self.libraries_view.clearSelection()
            self.libraries_view.setCurrentItem(None)
        QtWidgets.QTreeWidget.mousePressEvent(self.libraries_view, event)

    def _start_editor(self):
        if not self.editor:
            self.editor = editor.AssetEditor(self.core_index, self.library)

    def on_create_asset_clicked(self):
        """Wrap selected USD files into folders named after each file."""
        selected = self.libraries_view.selectedItems()
        if not selected:
            self._display_warning_message("Invalid Selection",
                                          "Please select USD files.")

        usd_list = self._get_usd_files_list(selected)

        self._start_editor()
        errored_files = self.editor.create_assets(usd_list)

        if errored_files:
            msg = "\n".join(file for file in errored_files)
            self._display_warning_message("Asset Exists",
                                          f"Please select only USD files that does not structured correctly."
                                          f"\nSkipped:\n{msg}")

        self._reload_libraries_view()

    def on_group_variant_clicked(self):
        """
        Group selected USD files into a single asset with variants.
        Ensures all selected files belong to the same directory before
        building a variant set.
        """
        selected = self.libraries_view.selectedItems()
        if not selected:
            self._display_warning_message("Invalid Selection",
                                          "Please select only USD files from the same folder.")
            return
        first_parent = selected[0].parent()

        if not all(item.parent() == first_parent for item in selected):
            self._display_warning_message("Invalid Selection",
                                          "Variant USD files must be selected from the same folder.")
            return

        usd_files = self._get_usd_files_list(selected)

        self._start_editor()
        self.editor.create_asset_with_variant(usd_files)
        self._reload_libraries_view()

    def _get_usd_files_list(self, selected):
        """Return a list of USD file paths extracted from the selected items' metadata."""
        usd_list = []
        for item in selected:
            metadata = item.data(0, QtCore.Qt.UserRole)
            usd_file = metadata.get("usd_file")
            usd_list.append(usd_file)
        return usd_list

    def _display_warning_message(self, title, message):
        """Display a warning message dialog with the given title and message."""
        QtWidgets.QMessageBox.warning(self, title, message)
