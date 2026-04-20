import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.1"


class AixlogConan(ConanFile):
    name = "aixlog"
    description = (
        "Single-header C++ logging library with pluggable sinks and severity levels, "
        "for applications that need lightweight logging without external runtime dependencies."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/badaix/aixlog"
    topics = ("android-log", "eventlog", "header-only", "logcat", "logging", "macos-log", "outputdebugstring", "syslog")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # master branch is on 3.10 but changes have not been released
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.10"
        tc.cache_variables["BUILD_EXAMPLE"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
