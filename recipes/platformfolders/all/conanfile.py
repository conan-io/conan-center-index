from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class PlatformFoldersConan(ConanFile):
    name = "platformfolders"
    license = "MIT"
    homepage = "https://github.com/sago007/PlatformFolders"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C++ library to look for special directories like \"My Documents\" and \"%APPDATA%\" so that you do not need to write Linux, Windows or Mac OS X specific code"
    topics = ("multi-platform", "xdg", "standardpaths", "special-folders")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        if not self.settings.os in ("Windows", "Macos", "Linux"):
            raise ConanInvalidConfiguration("This library only supports Windows, macOS and Linux")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PLATFORMFOLDERS_BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["platform_folders"]

