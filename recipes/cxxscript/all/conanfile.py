import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0"


class CxxscriptConan(ConanFile):
    name = "cxxscript"
    description = (
        "A modern, embeddable C++ scripting engine for running .script "
        "procedures from a host application"
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://slightlabs.github.io/CxxScript/"
    topics = ("scripting", "interpreter", "embeddable", "cpp17")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # ConanCenter builds library-only packages: skip GoogleTest (fetched
        # over the network) and the demo executables.
        tc.cache_variables["CXXSCRIPT_BUILD_TESTS"] = False
        tc.cache_variables["CXXSCRIPT_BUILD_EXAMPLES"] = False
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # The upstream build exports its own CMake package config files;
        # Conan's CMakeDeps generates the ones consumers actually use.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["CxxScript"]
        self.cpp_info.set_property("cmake_file_name", "CxxScript")
        self.cpp_info.set_property("cmake_target_name", "CxxScript::CxxScript")
        self.cpp_info.resdirs = ["share/CxxScript"]
