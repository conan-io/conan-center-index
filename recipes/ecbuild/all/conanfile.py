from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class EcbuildConan(ConanFile):
    name = "ecbuild"
    description = "A build system built on top of CMake by ECMWF"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ecmwf/ecbuild"
    topics = ("cmake", "build-system", "ecmwf", "build-tool")
    
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Remove empty share/man/man1 directory if exists, etc. Or maybe clean up unwanted files
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))

    def package_info(self):
        self.cpp_info.libs = []
        
        # It's a tool, but we might want to expose it to CMakeToolchain.
        # Find path to ecbuildConfig.cmake
        self.cpp_info.builddirs.append(os.path.join("share", "ecbuild", "cmake"))
        
        # In Conan 2, packages that want to be found via CMakeDeps usually set:
        self.cpp_info.set_property("cmake_file_name", "ecbuild")
        self.cpp_info.set_property("cmake_target_name", "ecbuild::ecbuild")
        
        # Make the scripts in bin available on the path
        self.cpp_info.bindirs = ["bin"]
