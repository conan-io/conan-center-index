import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"


class SocketcanCanaryConan(ConanFile):
    name = "canary"
    description = "A lightweight implementation of Linux SocketCAN bindings for ASIO/Boost.ASIO"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0 license"
    homepage = "https://github.com/djarek/canary"
    topics = ("socketcan", "canary")

    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "14.1",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can not be used on Windows.")

    def requirements(self):
        self.requires("boost/1.74.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.requires = ["boost::headers"]
        self.cpp_info.set_property("cmake_file_name", "canary")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_target_name", "canary::canary")
