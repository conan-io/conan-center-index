from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class GaiaConan(ConanFile):
    name = "gaia-ecs"
    description = "A simple and powerful entity component system (ECS) written in C++17 "
    topics = ("gamedev", "performance", "entity", "ecs")
    homepage = "https://github.com/richardbiely/gaia-ecs"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "10",
            "clang": "7.0",
            "apple-clang": "10.0",
            "intel-cc": "2021.2"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        if self.settings.os in ["FreeBSD", "Linux"]:
            self.cpp_info.system_libs = ["pthread"]
        
        self.cpp_info.set_property("cmake_file_name", "gaia")
        self.cpp_info.set_property("cmake_target_name", "gaia::gaia")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: remove when v1 support drops
        self.cpp_info.names["cmake_find_package"] = "gaia"
        self.cpp_info.names["cmake_find_package_multi"] = "gaia"
