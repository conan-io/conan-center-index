from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools import files
from conan import ConanFile
import os
import textwrap

required_conan_version = ">=1.59.0"

class GTLabLoggingConan(ConanFile):
    name = "gtlab-logging"
    license = "BSD-3-Clause"
    author = "Martin Siggel <martin.siggel@dlr.de>"
    url = "https://github.com/dlr-gtlab/gt-logging"
    homepage = "https://github.com/dlr-gtlab/gt-logging"
    toppics = "logging", "qt"
    description = "Simple logging interface with qt support"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def generate(self):
        CMakeToolchain(self).generate()
        CMakeDeps(self).generate()


    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def build(self):    
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()


    def package(self):
        cmake = CMake(self)
        cmake.install()

        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.copy(self, "README.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        files.copy(self, os.path.join("LICENSES", "BSD-3-Clause.txt"), dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["GTlabLogging"]
        
        self.cpp_info.includedirs.append(os.path.join("include", "logging"))

        self.cpp_info.libdirs = ['lib', 'lib/logging']

        if self.settings.build_type != "Debug":
            self.cpp_info.libs = ['GTlabLogging']
        else:
            self.cpp_info.libs = ['GTlabLogging-d']

        self.cpp_info.set_property("cmake_file_name", "GTlabLogging")
        self.cpp_info.set_property("cmake_target_name", "GTlab::Logging")
