from pathlib import Path

import hou


class HouAssetLoader:
    """Class to load USD asset inside a Houdini LOP network."""

    def __init__(self):
        self.lop_network = self._get_active_lop_network()
        self.displayed_stage = self._get_display_node()

    @staticmethod
    def _get_active_lop_network():
        """Retrieve the currently active LOP network from the Scene Viewer."""
        viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
        if not viewer:
            raise RuntimeError("No Scene Viewer found")
        node = viewer.pwd()
        return node

    def _get_display_node(self) -> hou.node:
        """Return the node with the display flag set, or None if the stage is empty."""
        display_node = self.lop_network.displayNode()
        if not display_node:
            return None
        return display_node

    def create_asset_reference(self, reference_file) -> None:
        """Create an asset reference node in the LOP network for the selected USD file."""
        node_name = Path(reference_file).stem

        if self.displayed_stage:
            asset_reference = self.displayed_stage.createOutputNode("assetreference", node_name)
        else:
            asset_reference = self.lop_network.createNode("assetreference", node_name)
        asset_reference.parm("filepath").set(str(reference_file))
