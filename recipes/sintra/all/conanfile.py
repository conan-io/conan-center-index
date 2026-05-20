from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.0"


class SintraConan(ConanFile):
    name = "sintra"
    license = "BSD-2-Clause"
    homepage = "https://github.com/imakris/sintra"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Header-only C++20 IPC library using shared-memory ring buffers."
    topics = ("ipc", "shared-memory", "rpc", "pubsub", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SINTRA_BUILD_EXAMPLES"] = "OFF"
        tc.cache_variables["SINTRA_BUILD_TESTS"] = "OFF"
        tc.cache_variables["SINTRA_INSTALL"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "sintra")
        self.cpp_info.set_property("cmake_target_name", "sintra::sintra")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
