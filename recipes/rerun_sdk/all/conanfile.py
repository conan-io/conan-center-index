import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, rmdir, copy
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

required_conan_version = ">=2.0"

class Package(ConanFile):
    name = "rerun_sdk"

    homepage = "https://rerun.io/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Visualize streams of multimodal data. Free, fast, easy to use, and simple to integrate. Built in Rust."
    topics = ("visualization", "computer-vision", "robotics", "multimodal")
    license = ("Apache-2.0", "MIT")
    package_type = "library"

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
        elif self.settings.arch == "armv8":
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
        self.requires("arrow/24.0.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["RERUN_DOWNLOAD_AND_BUILD_ARROW"] = "OFF"
        tc.variables["RERUN_ARROW_LINK_SHARED"] = bool(self.dependencies["arrow"].options.shared)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE-*", self.source_folder, os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        # Remove installed cmake config files
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["rerun_sdk", self._get_additional_lib()]
        self.cpp_info.requires = ["arrow::libarrow"]

        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "IOKit", "Security"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "Crypt32",
                "Iphlpapi",
                "Ncrypt",
                "Netapi32",
                "ntdll",
                "Pdh",
                "PowrProf",
                "Psapi",
                "Secur32",
                "Userenv",
                "ws2_32",
            ]
