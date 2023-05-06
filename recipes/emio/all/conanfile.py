from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class EmioConan(ConanFile):
    name = "emio"
    description = "A character input/output library for embedded systems."
    topics = ("format", "scan", "header-only")
    homepage = "https://github.com/viatorus/emio"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "Visual Studio": "16.2",
            "msvc": "19.22",
            "clang": "13",
            "apple-clang": "13",
        }

    @property
    def _min_cppstd(self):
        return 20

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "emio"
        self.cpp_info.filenames["cmake_find_package_multi"] = "emio"
        self.cpp_info.names["cmake_find_package"] = "emio"
        self.cpp_info.names["cmake_find_package_multi"] = "emio"
