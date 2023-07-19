import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CozConan(ConanFile):
    name = "coz"
    description = "Causal profiler, uses performance experiments to predict the effect of optimizations"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://coz-profiler.org"
    topics = ("profiler", "causal")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def requirements(self):
        self.requires("libelfin/0.3")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        compiler = self.settings.compiler
        compiler_version = Version(self.settings.compiler.version)
        if self.settings.os == "Macos" or is_msvc(self) or (compiler == "gcc" and compiler_version < "5.0"):
            raise ConanInvalidConfiguration(f"coz doesn't support compiler: {self.settings.compiler} on OS: {self.settings.os}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # https://github.com/plasma-umass/coz/#cmake
        self.cpp_info.set_property("cmake_file_name", "coz-profiler")
        self.cpp_info.set_property("cmake_target_name", "coz::coz")

        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "coz-profiler"
        self.cpp_info.filenames["cmake_find_package_multi"] = "coz-profiler"
        self.cpp_info.names["cmake_find_package"] = "coz"
        self.cpp_info.names["cmake_find_package_multi"] = "coz"
