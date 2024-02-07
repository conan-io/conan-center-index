from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class BatteryEmbedConan(ConanFile):
    name = "battery-embed"
    description = "A CMake/C++20 library to embed resource files at compile time"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/batterycenter/embed"
    topics = ("embed")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "12",
            "apple-clang": "13",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "CMakeLists.txt", self.source_folder, os.path.join(self.package_folder, "lib", "cmake", "battery-embed"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []

        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "battery-embed", "CMakeLists.txt")])
