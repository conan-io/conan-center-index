import os
import shutil

from conan import ConanFile
from conan.tools.files import copy, get, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0.0"

class ZserioConanFile(ConanFile):
    name = "zserio"
    description = "Zserio C++ Runtime Library"
    license = "BSD-3 Clause"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://zserio.org"
    topics = ("zserio", "C++", "serialization")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if Version(self.version) < "2.13.0":
            raise ConanInvalidConfiguration("Minimum available version is 2.13.0")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["runtime"],
            pattern="runtime_libs/cpp/*", strip_root=True)
        shutil.move("cpp/zserio", ".")
        shutil.move("cpp/CMakeLists.txt", ".")
        shutil.rmtree("cpp")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        get(self, **self.conan_data["sources"][self.version]["compiler"], pattern="zserio.jar")

    def package(self):
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"))
        copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "*.a", self.build_folder, os.path.join(self.package_folder, "lib"))

        copy(self, "zserio.jar", self.build_folder, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.components["ZserioCppRuntime"].libs = collect_libs(self)

        self.buildenv_info.define("ZSERIO_JAR_FILE", os.path.join(self.package_folder, "bin", "zserio.jar"))
