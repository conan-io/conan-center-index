import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir

required_conan_version = ">=2.1"


class NoqtisConan(ConanFile):
    name = "noqtis"
    description = "Post-quantum signing, KEMs and sealed input records in C11"
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rootcoder007/noqtis"
    topics = ("cryptography", "post-quantum", "ml-dsa", "ml-kem", "slh-dsa", "signatures")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tool": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tool": False,
    }
    languages = "C"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NQSHARED"] = bool(self.options.shared)
        tc.cache_variables["NQCLI"] = bool(self.options.tool)
        tc.cache_variables["NQTESTS"] = False
        tc.cache_variables["NQWERROR"] = False
        tc.cache_variables["NQMAN"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "noqtis")
        self.cpp_info.set_property("cmake_target_name", "noqtis::noqtis")
        self.cpp_info.set_property("pkg_config_name", "noqtis")
        self.cpp_info.libs = ["noqtis"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["bcrypt", "ws2_32"]
