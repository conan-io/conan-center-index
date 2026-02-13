import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir

required_conan_version = ">=2.4"


class UsrsctpConan(ConanFile):
    name = "usrsctp"
    description = " A portable SCTP userland stack"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sctplab/usrsctp"
    topics = ("network", "sctp")

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
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["sctp_debug"] = False
        tc.variables["sctp_werror"] = False
        tc.variables["sctp_build_shared_lib"] = self.options.shared
        tc.variables["sctp_build_programs"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        # Disable net/route.h for iOS (header not available in iOS SDK)
        tc.variables["USE_NET_ROUTE_H"] = self.settings.os != "iOS"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "usrsctp")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        suffix = "_import" if self.settings.os == "Windows" and self.options.shared else ""
        self.cpp_info.libs = ["usrsctp" + suffix]
