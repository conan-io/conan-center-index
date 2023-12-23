from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class CAresConan(ConanFile):
    name = "c-ares"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C library for asynchronous DNS requests"
    topics = ("dns", "resolver", "async")
    homepage = "https://c-ares.haxx.se/"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
    }

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CARES_STATIC"] = not self.options.shared
        tc.variables["CARES_SHARED"] = self.options.shared
        tc.variables["CARES_BUILD_TESTS"] = False
        tc.variables["CARES_MSVC_STATIC_RUNTIME"] = False
        tc.variables["CARES_BUILD_TOOLS"] = self.options.tools
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "c-ares")
        self.cpp_info.set_property("cmake_target_name", "c-ares::cares")
        self.cpp_info.set_property("pkg_config_name", "libcares")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["cares"].libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.components["cares"].defines.append("CARES_STATICLIB")
        if self.settings.os == "Linux":
            self.cpp_info.components["cares"].system_libs.append("rt")
            if Version(self.version) >= "1.23.0":
                self.cpp_info.components["cares"].system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.components["cares"].system_libs.extend(["ws2_32", "advapi32"])
            if Version(self.version) >= "1.18.0":
                self.cpp_info.components["cares"].system_libs.append("iphlpapi")
        elif is_apple_os(self):
            self.cpp_info.components["cares"].system_libs.append("resolv")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["pkg_config"] = "libcares"
        self.cpp_info.components["cares"].names["cmake_find_package"] = "cares"
        self.cpp_info.components["cares"].names["cmake_find_package_multi"] = "cares"
        self.cpp_info.components["cares"].names["pkg_config"] = "libcares"
        self.cpp_info.components["cares"].set_property("cmake_target_name", "c-ares::cares")
        self.cpp_info.components["cares"].set_property("pkg_config_name", "libcares")
        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
