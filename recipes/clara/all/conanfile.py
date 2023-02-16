import os
from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

required_conan_version = ">=1.46.0"

class ClaraConan(ConanFile):
    name = "clara"
    description = "A simple to use, composable, command line parser for C++ 11 and beyond"
    homepage = "https://github.com/catchorg/Clara"
    topics = ("clara", "cli", "cpp11", "command-parser")
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    no_copy_source = True
    deprecated = "lyra"

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"), keep_path=True)

    def package_id(self):
        self.info.clear()
