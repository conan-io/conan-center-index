import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version


required_conan_version = ">=2.0.9"


class NablaNetConan(ConanFile):
    name = "nablanet"
    description = "A dependency-free C++20 multilayer-perceptron learning library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Towstar/Nabla-Net"
    topics = ("machine-learning", "neural-network", "cpp20", "education")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, "20")

    def build_requirements(self):
        if self.settings.compiler == "msvc" and Version(str(self.settings.compiler.version)) >= "195":
            self.tool_requires("cmake/[>=4.4.3 <5]")
        else:
            self.tool_requires("cmake/[>=3.21 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["BUILD_TESTING"] = False
        toolchain.cache_variables["NABLANET_BUILD_EXAMPLES"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["NablaNet"]
        self.cpp_info.set_property("cmake_file_name", "NablaNet")
        self.cpp_info.set_property("cmake_target_name", "NablaNet::NablaNet")
