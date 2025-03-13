import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class HidapiConan(ConanFile):
    name = "hidapi"
    description = "HIDAPI is a multi-platform library which allows an application to interface " \
                  "with USB and Bluetooth HID-Class devices on Windows, Linux, FreeBSD, and macOS."
    topics = ("libusb", "hid-class", "bluetooth")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libusb/hidapi"
    license = "GPL-3-or-later", "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "build_hidapi_libusb": [True, False],
        "build_hidapi_hidraw": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "build_hidapi_libusb": True,
        "build_hidapi_hidraw": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.build_hidapi_libusb
            del self.options.build_hidapi_hidraw

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("build_hidapi_libusb"):
            self.requires("libusb/1.0.26")
            self.requires("libiconv/1.17")
        if self.settings.os == "Linux" and self.options.build_hidapi_hidraw:
            self.requires("libudev/system")

    def validate(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            if not self.options.build_hidapi_libusb and not self.options.build_hidapi_hidraw:
                raise ConanInvalidConfiguration(
                    "At least one of 'build_hidapi_libusb' or 'build_hidapi_hidraw' must be enabled"
                )

    def build_requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # TODO: Remove after fixing https://github.com/conan-io/conan/issues/12012
        # Needed for https://github.com/libusb/hidapi/blob/hidapi-0.14.0/libusb/CMakeLists.txt#L34
        tc.variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Move project() right after cmake_minimum_required()
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "project(hidapi LANGUAGES C)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        " FATAL_ERROR)", " FATAL_ERROR)\nproject(hidapi LANGUAGES C)")

    def build(self):
        self._patch_sources()
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
        self.cpp_info.set_property("cmake_file_name", "hidapi")

        # See https://github.com/libusb/hidapi/blob/hidapi-0.14.0/src/CMakeLists.txt#L95-L169
        # for details about the hidapi::hidapi target alias.

        if self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.build_hidapi_libusb:
                self.cpp_info.components["libusb"].set_property("pkg_config_name", "hidapi-libusb")
                self.cpp_info.components["libusb"].set_property("cmake_target_name", "hidapi::libusb")
                if not self.options.build_hidapi_hidraw:
                    self.cpp_info.components["libusb"].set_property("cmake_target_aliases", ["hidapi::hidapi"])
                self.cpp_info.components["libusb"].libs = ["hidapi-libusb"]
                self.cpp_info.components["libusb"].includedirs.append(os.path.join("include", "hidapi"))
                self.cpp_info.components["libusb"].requires = ["libusb::libusb", "libiconv::libiconv"]
                self.cpp_info.components["libusb"].system_libs = ["pthread", "dl", "rt"]
            if self.options.build_hidapi_hidraw:
                self.cpp_info.components["hidraw"].set_property("pkg_config_name", "hidapi-hidraw")
                self.cpp_info.components["hidraw"].set_property("cmake_target_name", "hidapi::hidraw")
                self.cpp_info.components["hidraw"].set_property("cmake_target_aliases", ["hidapi::hidapi"])
                self.cpp_info.components["hidraw"].libs = ["hidapi-hidraw"]
                self.cpp_info.components["hidraw"].includedirs.append(os.path.join("include", "hidapi"))
                if self.settings.os == "Linux":
                    self.cpp_info.components["hidraw"].requires = ["libudev::libudev"]
                self.cpp_info.components["hidraw"].system_libs = ["pthread", "dl"]
        elif is_apple_os(self):
            self.cpp_info.set_property("cmake_target_name", "hidapi::darwin")
            self.cpp_info.set_property("cmake_target_aliases", ["hidapi::hidapi"])
            self.cpp_info.libs = ["hidapi"]
            self.cpp_info.includedirs.append(os.path.join("include", "hidapi"))
            self.cpp_info.frameworks.extend(["IOKit", "CoreFoundation", "AppKit"])
        else:
            self.cpp_info.set_property("cmake_target_name", "hidapi::winapi")
            self.cpp_info.set_property("cmake_target_aliases", ["hidapi::hidapi"])
            self.cpp_info.libs = ["hidapi"]
            self.cpp_info.includedirs.append(os.path.join("include", "hidapi"))
