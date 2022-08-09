from os import path

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.47.0"


class SamariumConan(ConanFile):
    name = "samarium"
    description = "2-D physics simulation library"
    homepage = "https://strangequark1041.github.io/samarium/"
    url = "https://github.com/conan-io/conan-center-index/"
    license = "MIT"
    topics = ("cpp20", "physics", "2d", "simulation")
    generators = "CMakeDeps", "CMakeToolchain"
    requires = "fmt/9.0.0", "sfml/2.5.1", "range-v3/0.12.0", "stb/cci.20210910", "tl-expected/20190710"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [
        True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "patches/*"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11.0",
            "Visual Studio": "16",
            "clang": "13",
            "apple-clang": "13",
        }

    def source(self):
        get(self, **self.conan_data["sources"]
            [str(self.version)], strip_root=True)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.version == "1.0.0" and self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos not supported for v1.0.0")

        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warn(
                "Unknown compiler, assuming it supports at least C++20")
            return

        version = Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++20")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.folders.source_folder,
             dst=path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["samarium"]
