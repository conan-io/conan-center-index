from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import cross_building
from conan.tools.files import collect_libs, copy, rename, get, apply_conandata_patches, export_conandata_patches, replace_in_file, rmdir, rm
from conan.tools.microsoft import check_min_vs, msvc_runtime_flag, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

from conan.errors import ConanInvalidConfiguration
from conan import ConanFile
from conan.tools.apple import is_apple_os

import os
import textwrap

required_conan_version = ">=1.53"


class STLinkConan(ConanFile):
    name = "stlink"
    description = "Open source STM32 MCU programming toolset"
    topics = ("stm32", "mcu", "usb")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stlink-org/stlink"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if self.settings.os in ["Linux", "Android"]:
            self.options["libusb"].enable_udev = False

    def requirements(self):
        self.requires("libusb/1.0.26")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "stlink")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        if self.options.shared:
            for ext in [".lib", ".a"]:
                rm(self, "*"+ext, os.path.join(self.package_folder, "lib"))
        else:
            for ext in [".dll", ".so*", ".dylib"]:
                rm(self, "*"+ext, os.path.join(self.package_folder, "lib"))


    def package_info(self):
        #self.cpp_info.libs = ["stlink"]
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs = ["include/stlink"]
