from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4"


class iniparserConan(ConanFile):
    name = "iniparser"
    description = "iniParser is a simple C library offering ini file parsing services."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://iniparser.gitlab.io/iniparser/"
    topics = ("ini", "parser", "configuration", "file")

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
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_STATIC_LIBS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["libiniparser" if is_msvc(self) and not self.options.shared else "iniparser"]

        self.cpp_info.set_property("cmake_target_name", "iniparser-shared" if self.options.shared else "iniparser-static")
        self.cpp_info.includedirs.append(os.path.join("include", "iniparser"))
