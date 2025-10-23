from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir

import os

required_conan_version = ">=2.0.0"


class OpenAPVConan(ConanFile):
    name = "openapv"
    description = "Open Advanced Professional Video Codec reference implementation."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AcademySoftwareFoundation/openapv"
    topics = ("openapv", "image", "picture", "video", "codec")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OAPV_APP_STATIC_BUILD"] = not self.options.shared
        tc.cache_variables["OAPV_BUILD_STATIC_LIB"] = not self.options.shared
        tc.cache_variables["OAPV_BUILD_SHARED_LIB"] = self.options.shared
        tc.cache_variables["ENABLE_TESTS"] = False
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "msvcp*.dll", os.path.join(self.package_folder, "bin"))
        rm(self, "concrt*.dll", os.path.join(self.package_folder, "bin"))
        rm(self, "vcruntime*.dll", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenAPV")
        self.cpp_info.set_property("pkg_config_name", "OpenAPV")

        self.cpp_info.libs = ["oapv"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.libdirs = ["lib/oapv/import"]
        elif not self.options.shared:
            self.cpp_info.libdirs = ["lib/oapv"]

        if not self.options.shared:
            self.cpp_info.defines.append("OAPV_STATIC_DEFINE")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
