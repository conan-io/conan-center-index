from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class PlatformFoldersConan(ConanFile):
    name = "platformfolders"
    license = "MIT"
    homepage = "https://github.com/sago007/PlatformFolders"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C++ library to look for special directories like My Documents and APPDATA so that you do not need to write Linux, Windows or Mac OS X specific code"
    topics = ("multi-platform", "xdg", "standardpaths", "special-folders")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        if is_msvc(self) and self.options.shared:
            # See https://github.com/sago007/PlatformFolders/pull/29
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared libraries with MSVC.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PLATFORMFOLDERS_BUILD_TESTING"] = False
        tc.variables["PLATFORMFOLDERS_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["PLATFORMFOLDERS_ENABLE_INSTALL"] = True
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
        self.cpp_info.set_property("cmake_file_name", "platform_folders")
        self.cpp_info.set_property("cmake_target_name", "sago::platform_folders")
        self.cpp_info.set_property("cmake_target_aliases", ["platform_folders"])
