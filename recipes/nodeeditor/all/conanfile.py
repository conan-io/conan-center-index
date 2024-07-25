from conan import ConanFile
from conan.tools.files import get

class NodeEditorConan(ConanFile):
    name = "nodeeditor"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
