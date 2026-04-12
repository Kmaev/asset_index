from collections.abc import Iterator
from pathlib import Path

import hou

from asset_index.asset_import import base_import_kit
from importlib import reload

reload(base_import_kit)

class HoudiniKitImporter(base_import_kit.BaseKitImporter):
    """
    Houdini Kit Importer, adds an interruptible progress bar during asset conversion.
    """

    def iterate_with_progress_bar(self, assets: list[Path]) -> Iterator[Path]:
        """
        Adds and updates an interruptible Houdini progress bar.
        """
        total = len(assets)
        with hou.InterruptableOperation("Generating thumbnails", open_interrupt_dialog=True) as op:
            for i, asset in enumerate(assets):
                op.updateLongProgress((i + 1) / total)
                
                yield asset
