from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeDeps, CMakeToolchain
import os


required_conan_version = ">=2.4"

class AkashaConan(ConanFile):
    name = "akasha"
    description = "High-performance hierarchical data store with memory-mapped file persistence"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yawin123/Akasha"
    license = "MIT"
    topics = ("libraries", "cpp", "data-store", "memory-mapped")
    implements = ["auto_shared_fpic"]
    languages = "C++"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "static-library"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def requirements(self):
        self.requires("boost/1.90.0")
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def validate(self):
        check_min_cppstd(self, 23)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["akasha"]
