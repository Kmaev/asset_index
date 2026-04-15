name = "asset_index"
version = "1.0.0"
build_command = "python {root}/build.py {install}"

requires = ["PySide6_Addons", "~usd"]


def commands():
    global env

    env.PYTHONPATH.append("{root}/python")
