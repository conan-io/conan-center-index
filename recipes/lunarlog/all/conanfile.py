from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, copy, rmdir
from conan.tools.layout import basic_layout
import os


class LunarLogConan(ConanFile):
    name = "lunarlog"
    description = "Header-only C++11 structured logging library with message templates. Inspired by Serilog."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LunarECL/LunarLog"
    topics = ("logging", "structured-logging", "header-only", "cpp11", "message-templates", "serilog")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LUNARLOG_BUILD_EXAMPLES"] = False
        tc.cache_variables["LUNARLOG_BUILD_TESTS"] = False
        tc.generate()

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "LunarLog")
        self.cpp_info.set_property("cmake_target_name", "LunarLog::LunarLog")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
