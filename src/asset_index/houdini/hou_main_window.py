from importlib import reload

from asset_index.houdini import hou_asset_loader
from asset_index.ui import main_window

reload(main_window)
reload(hou_asset_loader)


class HouMainWindow(main_window.AssetIndex):
    def __init__(self, parent):
        super(HouMainWindow, self).__init__(parent=parent)

        self.asset_loader = hou_asset_loader.HouAssetLoader()

    def load_asset(self, asset_path):
        self.asset_loader.import_asset(asset_path)


app_win = None


def show_houdini():
    import hou
    global app_win
    app_win = HouMainWindow(parent=hou.qt.mainWindow())
    app_win.show()
    return app_win
