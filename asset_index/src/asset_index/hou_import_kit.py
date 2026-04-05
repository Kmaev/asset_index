from importlib import reload

import hou

from asset_index import base_import_kit

reload(base_import_kit)


class HoudiniKitImporter(base_import_kit.BaseKitImporter):
    def iterate_with_progress_bar(self, assets):
        total = len(assets)
        with hou.InterruptableOperation("Generating thumbnails", open_interrupt_dialog=True) as op:
            for i, asset in enumerate(assets):
                op.updateLongProgress(i / total)
                yield asset
