
from conan import ConanFile
from conan.tools.files import copy

required_conan_version = ">=2.0.9"


class LIBRAConan(ConanFile):
    name = "libra"
    exports_sources = ["cmake/libra/*.cmake"]
    description = ("Reusable C/C++ build automation in the spirit of the "
                   "world's second most successful plumber")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https: // github.com/jharwell/libra"
    topics = ("buildsystems", "unit testing")
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.31]")


def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self,
             pattern="*.cmake",
             src=self.source_folder,
             dst=self.package_folder,
             excludes=["*/package/*.cmake",
                       "*/arm-*.cmake"])

    def package_info(self):
        self.cpp_info.builddirs = ["cmake"]
