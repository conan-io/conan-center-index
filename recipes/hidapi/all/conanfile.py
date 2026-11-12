from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=2.1"


class HidapiConan(ConanFile):
    name = "hidapi"
    package_type = "library"
    description = "HIDAPI is a multi-platform library which allows an application to interface " \
                  "with USB and Bluetooth HID-Class devices on Windows, Linux, FreeBSD, and macOS."
    topics = ("libusb", "hid-class", "bluetooth")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libusb/hidapi"
    license = "GPL-3.0-or-later", "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libusb/1.0.26")
        if self.settings.os == "Linux":
            self.requires("libudev/system")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("libtool/2.4.7")
            if self.settings.os in ["Linux", "FreeBSD"] and not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/[>=1.9.3 <3]")
            if self.settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libusb"].set_property("pkg_config_name", "hidapi-libusb")
            self.cpp_info.components["libusb"].libs = ["hidapi-libusb"]
            self.cpp_info.components["libusb"].requires = ["libusb::libusb"]
            self.cpp_info.components["libusb"].system_libs = ["pthread", "dl", "rt"]

            self.cpp_info.components["hidraw"].set_property("pkg_config_name", "hidapi-hidraw")
            self.cpp_info.components["hidraw"].libs = ["hidapi-hidraw"]
            if self.settings.os == "Linux":
                self.cpp_info.components["hidraw"].requires = ["libudev::libudev"]
            self.cpp_info.components["hidraw"].system_libs = ["pthread", "dl"]
        else:
            self.cpp_info.libs = ["hidapi"]
            if is_apple_os(self):
                self.cpp_info.frameworks.extend(["IOKit", "CoreFoundation", "AppKit"])
