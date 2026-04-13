import json
from pathlib import Path
from typing import Any

from asset_index.utils import import_utils


class LibraryIndex:
    """Class to manage asset library indexing and metadata"""

    def __init__(self):
        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))
        self.libraries_data_file = self.global_asset_lib / "libraries.json"

        self._all_libraries = None

    def list_all_libraries(self) -> list:
        """Return all library folder names. Searches the file system."""
        if self._all_libraries is None:
            self._all_libraries = sorted([folder.name for folder in self.global_asset_lib.iterdir() if
                                          folder.is_dir()])

        return self._all_libraries

    def list_imported_libraries(self) -> list:
        """Return libraries registered in the global metadata file."""
        with open(self.libraries_data_file, "r") as f:
            libraries_list = json.load(f)
        imported_libraries = sorted(libraries_list)
        return imported_libraries

    def list_unimported_libraries(self) -> list:
        """Return libraries not yet imported."""
        imported_libraries = self.list_imported_libraries()
        all_libraries = self.list_all_libraries()
        not_imported_libraries = [lib for lib in all_libraries if lib not in imported_libraries]
        return not_imported_libraries

    def load_library_catalog(self, library) -> Any | None:
        """Load and return catalog data for a given library."""
        current_lib_path = self.global_asset_lib / f"{library}/library_catalog.json"
        if not current_lib_path.is_file():
            return None
        else:
            with open(current_lib_path, "r") as f:
                selected_catalog = json.load(f)
            return selected_catalog[library]
