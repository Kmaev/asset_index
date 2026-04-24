# Copyright (c) 2026 Kristina Maevskaya
# Asset Browser — portfolio project.
from collections.abc import Iterator
from pathlib import Path

from PySide6 import QtWidgets, QtCore

from asset_index.asset_import import base_import_kit


class QtKitImporter(base_import_kit.BaseKitImporter):
    """Qt Kit Importer, adds an interruptible progress dialog during asset conversion."""

    def iterate_with_progress_bar(self, assets: list[Path]) -> Iterator[Path]:
        """
        Report render progress.

        Args:
            assets: List of USD file paths to process.

        Returns:
            Iterator: Yields each asset.
        """
        total = len(assets)
        progress = QtWidgets.QProgressDialog("Generating thumbnails", "Cancel", 0, total)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        progress.setFixedSize(300, 120)
        progress.setMinimumDuration(0)
        try:
            for i, asset in enumerate(assets):
                if progress.wasCanceled():
                    self.interrupted = True
                    return

                progress.setValue(i + 1)
                progress.setLabelText(f"{asset.name}")
                QtWidgets.QApplication.processEvents()

                yield asset

        finally:
            progress.close()
