from asset_index.houdini import hou_asset_loader
from asset_index.ui import main_window


class HouMainWindow(main_window.AssetIndex):
    """
    Houdini-specific implementation of the AssetIndex UI.

    Extends the base UI with Houdini asset loading via HouAssetLoader.
    """

    def __init__(self, parent):
        """
        Initialize the Houdini AssetIndex window.

        Args:
            parent: Parent widget.
        """
        super(HouMainWindow, self).__init__(parent=parent)

        self.asset_loader = hou_asset_loader.HouAssetLoader()

    def load_asset(self, asset_path) -> None:
        """
        Load a USD asset into Houdini LOP network.

        Args:
            asset_path: USD asset file path.
        """
        self.asset_loader.create_asset_reference(asset_path)


app_win = None


def show_houdini():
    """
    Create and display the AssetIndex window in Houdini.

    Returns:
        HouMainWindow: The created window instance.
    """
    import hou
    global app_win
    app_win = HouMainWindow(parent=hou.qt.mainWindow())
    app_win.show()
    return app_win
