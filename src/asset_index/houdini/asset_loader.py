from pathlib import Path

import hou


class HouAssetLoader:
    def __init__(self, asset_path: list[str]):
        self.asset_path = asset_path
        self.lop_network = self._get_active_lop_network()
        self.displayed_stage = self._get_display_node()

    def import_assets(self):
        for asset in self.asset_path:
            self.create_asset_reference(self.displayed_stage, asset)

    @staticmethod
    def _get_active_lop_network():
        viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not viewer:
            raise RuntimeError("No Scene Viewer found")
        node = viewer.pwd()
        return node

    def _get_display_node(self):
        display_node = self.lop_network.displayNode()
        if not display_node:
            raise RuntimeError("No active stage found")
        return display_node

    @staticmethod
    def create_asset_reference(lop_input_node: hou.node, reference_file):
        node_name = Path(reference_file).stem
        asset_reference = lop_input_node.createOutputNode("assetreference", node_name)
        asset_reference.parm("filepath").set(reference_file)
