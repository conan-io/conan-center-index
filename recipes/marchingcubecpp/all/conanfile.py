from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.4"


class MarchingCubeCppConan(ConanFile):
    name = "marchingcubecpp"
    description = "A public domain/MIT header-only marching cube implementation in C++."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aparis69/MarchingCubeCpp"
    topics = ("graphics", "marching-cube", "header-only")
    package_type = "header-library"
    implements = ["auto_header_only"]
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "MC.h",  src=self.source_folder,  dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
