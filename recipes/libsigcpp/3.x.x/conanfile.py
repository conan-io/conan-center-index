from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, get,
    rename, rmdir
)
import glob
import os

required_conan_version = ">=2.1"


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0-only"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("callback",)

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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-3.0", "include", "*.h")):
            dst = os.path.join(self.package_folder, "include", "sigc++-3.0", os.path.basename(header_file))
            rename(self, header_file, dst)
        for dir_to_remove in ["cmake", "pkgconfig", "sigc++-3.0"]:
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sigc++-3")
        self.cpp_info.set_property("cmake_target_name", "sigc-3.0")
        self.cpp_info.set_property("pkg_config_name", "sigc++-3.0")

        self.cpp_info.components["sigc++"].includedirs = [os.path.join("include", "sigc++-3.0")]
        self.cpp_info.components["sigc++"].libs = ["sigc-3.0"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["sigc++"].system_libs.append("m")

        if not self.options.shared:
            self.cpp_info.components["sigc++"].defines = ["LIBSIGCXX_STATIC"]

        self.cpp_info.components["sigc++"].set_property("pkg_config_name", "sigc++-3.0")
