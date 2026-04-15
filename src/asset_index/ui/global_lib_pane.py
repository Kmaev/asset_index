from importlib import reload
from pathlib import Path

from PySide6 import QtWidgets, QtGui, QtCore

from asset_index.ui import asset_label, import_lib_pane

reload(asset_label)
reload(import_lib_pane)


class GlobalLib(QtWidgets.QFrame):
    """UI widget for browsing and importing assets into global library."""

    selected_lib_signal = QtCore.Signal(str)

    def __init__(self, core_index, parent=None):
        super(GlobalLib, self).__init__(parent=parent)

        self.import_library_frame = None
        self.core_index = core_index
        self.central_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.central_layout)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([150, 450])
        self.central_layout.addWidget(self.splitter)

        self.libraries = QtWidgets.QListWidget()
        self.populate_libraries_list()
        self.libraries.setCurrentRow(0)
        self.libraries.setMinimumWidth(100)
        self.splitter.addWidget(self.libraries)

        self.assets_stack = QtWidgets.QStackedWidget()
        self.splitter.addWidget(self.assets_stack)

        self.assets = QtWidgets.QListWidget()
        self.assets.setViewMode(QtWidgets.QListView.IconMode)
        self.assets.setResizeMode(QtWidgets.QListView.Adjust)
        self.assets.setWrapping(True)
        self.assets.setMinimumWidth(150)
        self.assets.setIconSize(QtCore.QSize(150, 150))

        self.assets.setMovement(QtWidgets.QListView.Static)
        self.assets.setUniformItemSizes(True)
        self.assets.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.assets.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.assets.setMinimumSize(10, 10)
        self.assets.mousePressEvent = self._list_mouse_press_event

        self.assets_stack.addWidget(self.assets)

        self.library_not_imported_frame = QtWidgets.QFrame()
        self.library_not_imported_layout = QtWidgets.QVBoxLayout()
        self.library_not_imported_layout.setAlignment(QtCore.Qt.AlignTop)
        self.library_not_imported_frame.setLayout(self.library_not_imported_layout)

        self.assets_stack.addWidget(self.library_not_imported_frame)

        self.library_not_imported = QtWidgets.QLineEdit()
        self.library_not_imported.setText("No assets found. Import the library to get started.")
        self.library_not_imported.setAlignment(QtCore.Qt.AlignCenter)
        self.library_not_imported_layout.addWidget(self.library_not_imported)

        self.import_library = QtWidgets.QPushButton("Import Library")
        self.library_not_imported_layout.addWidget(self.import_library)

        self.import_library_frame = import_lib_pane.ImportLibrary(self.core_index)

        self.assets_stack.addWidget(self.import_library_frame)

        self.populate_asset_labels()

        self.libraries.itemSelectionChanged.connect(self.populate_asset_labels)

        self.import_library.clicked.connect(self.on_start_import_clicked)
        self.import_library_frame.update_global_lib.connect(self.on_library_imported)
        self.selected_lib_signal.connect(self.import_library_frame.set_library)

    def get_selection(self, widget: QtWidgets.QListWidget) -> QtWidgets.QListWidgetItem:
        """Return selected item from widget."""
        return widget.selectedItems()[0]

    def populate_libraries_list(self) -> None:
        """Populate list with imported and available libraries."""
        imported_libraries = self.core_index.list_imported_libraries()
        all_libraries = self.core_index.list_all_libraries()

        for lib in imported_libraries:
            self._add_library_item(lib, self.libraries, imported=True)
        for lib in all_libraries:
            if lib not in imported_libraries:
                self._add_library_item(lib, self.libraries, imported=False)

    def _add_library_item(self, name, parent, imported=True) -> None:
        """Add library item with metadata."""
        item = QtWidgets.QListWidgetItem(parent)
        item.setText(name)
        metadata = {"imported": imported}
        item.setData(QtCore.Qt.UserRole, metadata)

    def populate_asset_labels(self):
        """Update asset view for selected library."""
        selected = self.get_selection(self.libraries).text()
        selected_catalog = self.core_index.load_library_catalog(selected)

        if not selected_catalog:
            self.assets_stack.setCurrentIndex(1)
            self.selected_lib_signal.emit(selected)
            return

        self.assets_stack.setCurrentIndex(0)
        self.assets.clear()

        for path in selected_catalog:
            item = QtWidgets.QListWidgetItem()
            widget = asset_label.AssetFrame(Path(path))

            item.setSizeHint(widget.sizeHint())
            self.assets.addItem(item)
            self.assets.setItemWidget(item, widget)

    def on_start_import_clicked(self):
        """Switch to import view."""
        self.assets_stack.setCurrentIndex(2)

    def on_library_imported(self):
        """Refresh UI after library import."""
        self.populate_asset_labels()
        self.assets_stack.setCurrentIndex(0)

    def _list_mouse_press_event(self, event):
        """Clear selection on empty-space click."""
        item = self.assets.itemAt(event.pos())

        if item is None:
            self.assets.clearSelection()
            self.assets.setCurrentItem(None)
        QtWidgets.QListWidget.mousePressEvent(self.assets, event)
