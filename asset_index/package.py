name = "asset_index"
version = "1.0.0"
build_command = "python {root}/build.py {install}"

requires = ["PySide6_Addons", "~usd"]


def commands():
    global env

    env.PYTHONPATH.append("{root}/python")

    alias("asset_index", "python -m asset_index.ui.main_window")

