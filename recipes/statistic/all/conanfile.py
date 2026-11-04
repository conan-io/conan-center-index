from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class StatisticConan(ConanFile):
    name = "statistic"
    description = "Statistic library for Arduino includes sum, average, variance and std deviation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RobTillaart/Statistic"
    topics = ("arduino", "statistics", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support Visual Studio")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "Statistic.h",
            self.source_folder,
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
