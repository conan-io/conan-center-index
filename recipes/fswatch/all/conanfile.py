import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.apple import is_apple_os
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=2.0.9"


class WatcherConan(ConanFile):
    name = "fswatch"
    description = "A cross-platform file change monitor with multiple backends"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emcrisostomo/fswatch"
    topics = ("watch", "filesystem", "event", "monitor")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate_build(self):
        if is_apple_os(self) and cross_building(self):
            # INFO: Cmake error: "VERSION_GREATER_EQUAL" "9.0" Unknown arguments specified
            raise ConanInvalidConfiguration(f"{self.ref} does not support cross-building on {self.settings.os}")

    def validate(self):
        check_min_cppstd(self, 11)
        if is_msvc(self):
            # INFO: fswatch requires pthread always and fails CMake when using MSVC
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC due pthread requirement.")

    def requirements(self):
        self.requires("libgettext/0.22")

    def build_requirements(self):
        self.tool_requires("gettext/0.22.5")

    def _apply_patches(self):
        # Remove hardcoded CXX standard
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 11)",
                        "")

        # Dont compile tests
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory(test/src)",
                        "")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._apply_patches()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "COPYING*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["fswatch"]
        self.cpp_info.set_property("cmake_file_name", "fswatch")
        self.cpp_info.set_property("cmake_target_name", "fswatch::fswatch")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "CoreServices"]
