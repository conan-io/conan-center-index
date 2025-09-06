import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class Package(ConanFile):
    name = "rerun_sdk"

    homepage = "https://rerun.io/"
    url = "https://github.com/rerun-io/rerun"
    description = "Visualize streams of multimodal data. Free, fast, easy to use, and simple to integrate. Built in Rust."
    topics = ("visualization", "computer-vision", "robotics", "multimodal")
    license = ("Apache-2.0", "MIT")

    settings = "os", "arch", "compiler", "build_type"

    implements = ["auto_shared_fpic"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def _get_additional_lib(self):
        if self.settings.arch == "x86_64":
            if self.settings.os == "Linux":
                return "librerun_c__linux_x64.a"
            elif self.settings.os == "Windows":
                return "rerun_c__win_x64.lib"
            elif self.settings.os == "Macos":
                return "librerun_c__macos_x64.a"
        elif self.settings.arch == "arm64":
            if self.settings.os == "Linux":
                return "librerun_c__linux_arm64.a"
            elif self.settings.os == "Macos":
                return "librerun_c__macos_arm64.a"

        return None

    def validate(self):
        if self._get_additional_lib() is None:
            raise ConanInvalidConfiguration(
                f"Unsupported combination of architecture {self.settings.arch} and os {self.settings.os}"
            )

    def requirements(self):
        self.requires("arrow/21.0.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["RERUN_DOWNLOAD_AND_BUILD_ARROW"] = "OFF"
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options["fPIC"]
        tc.variables["BUILD_SHARED_LIBS"] = self.options["shared"]
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Remove installed cmake config files
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        arrow_cmake_suffix = "shared" if self.options["arrow/*"].shared else "static"

        self.cpp_info.libs = [
            "rerun_sdk",
            self._get_additional_lib(),
            f"Arrow::arrow_{arrow_cmake_suffix}",
        ]
