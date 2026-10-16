import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir

required_conan_version = ">=2.0.9"


class LibkeepassConan(ConanFile):
    name = "libkeepass"
    description = "C++11 library for reading and writing KeePass (KDB and KDBX) password databases"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dkruempe/libkeepass"
    topics = ("keepass", "password", "database", "security", "kdbx", "kdb")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]

    def validate(self):
        check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/3.5.7")
        self.requires("zlib/1.3.2")
        self.requires("pugixml/1.16")
        self.requires("argon2/20190702")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBKEEPASS_CONAN_CREATE"] = "ON"  # disables the Conan CMake provider
        tc.variables["BUILD_TESTING"] = "OFF"
        tc.variables["LIBKEEPASS_BUILD_SHARED"] = "ON" if self.options.shared else "OFF"
        tc.variables["WARNINGS_AS_ERRORS"] = "OFF"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["libkeepass"]
        self.cpp_info.requires = [
            "openssl::openssl",
            "zlib::zlib",
            "pugixml::pugixml",
            "argon2::argon2",
        ]
        self.cpp_info.set_property("cmake_file_name", "libkeepass")
        self.cpp_info.set_property("cmake_target_name", "kruempelmann::libkeepass")
        self.cpp_info.set_property("cmake_target_aliases", ["libkeepass"])
        self.cpp_info.set_property("pkg_config_name", "libkeepass")
