import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.cmake.toolchain.blocks import is_apple_os
from conan.tools.files import get, copy, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class WatcherConan(ConanFile):
    name = "fswatch"
    description = "A cross-platform file change monitor with multiple backends: Apple OS X File System Events, *BSD kqueue, Solaris/Illumos File Events Notification, Linux inotify, Microsoft Windows and a stat()-based backend.."
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emcrisostomo/fswatch"
    topics = ("watch", "filesystem", "event", "header-only")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # self.settings.rm_safe("compiler.libcxx")
        # self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc":
            if Version(self.settings.compiler.version) < "6":
                raise ConanInvalidConfiguration("gcc < 6 is unsupported")

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
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fswatch"]
        self.cpp_info.set_property("cmake_file_name", "fswatch")
        self.cpp_info.set_property("cmake_target_name", "fswatch::fswatch")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]

        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreServices"])
