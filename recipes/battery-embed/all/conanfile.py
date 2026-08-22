from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.cmake import cmake_layout
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
    package_type = "build-scripts"
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
        copy(self, "embed.cmake", src=self.recipe_folder, dst=self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type
        del self.info.settings.os

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        copy(self, "embed.cmake", os.path.join(self.source_folder, os.pardir), self.recipe_folder)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "embed.cmake", self.recipe_folder, os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "CMakeLists.txt", self.source_folder, os.path.join(self.package_folder, "lib", "cmake", "battery-embed"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []

        self.cpp_info.set_property("cmake_target_name", "battery::embed")
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "embed.cmake")])
