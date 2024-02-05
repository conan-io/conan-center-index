from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
import os

class CLIConan(ConanFile):
    name = "cli"
    description = "A library for interactive command line interfaces in modern C++"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/daniele77/cli"
    topics = "cli-interface", "cpp14", "no-dependencies", "cli", "header-only"
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "14"

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "CLI")
        self.cpp_info.set_property("cmake_target_name", "CLI::CLI")
        self.cpp_info.set_property("pkg_config_name", "CLI")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CLI"
        self.cpp_info.names["cmake_find_package_multi"] = "CLI"
        self.cpp_info.names["pkg_config"] = "CLI"