# SPDX-License-Identifier: MIT
import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class PonceletConan(ConanFile):
    name = "poncelet"
    description = "A realistic, low-latency projectile & terminal-ballistics library for games"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/FelixMiddelhoff/poncelet"
    topics = ("ballistics", "physics", "simulation", "game-development")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    # Only the static poncelet::poncelet CMake target is packaged. Upstream's
    # PONCELET_SHARED option adds a second, un-aliased poncelet_shared target
    # meant for direct in-tree linking (see the upstream repo's Unity
    # binding), not something that maps onto Conan's shared/static option
    # model, so no `shared` option is exposed here.

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PONCELET_SHARED"] = False
        tc.variables["PONCELET_BUILD_TESTS"] = False
        tc.variables["PONCELET_BUILD_BENCH"] = False
        tc.variables["PONCELET_BUILD_EXAMPLES"] = False
        tc.variables["PONCELET_BUILD_DOCS"] = False
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="poncelet")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "poncelet")
        self.cpp_info.set_property("cmake_target_name", "poncelet::poncelet")
        self.cpp_info.set_property("pkg_config_name", "poncelet")
        self.cpp_info.libs = ["poncelet"]
