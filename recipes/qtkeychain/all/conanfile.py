from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os


required_conan_version = ">=2.0.9"
class PackageConan(ConanFile):
    name = "qtkeychain"
    description = "Platform-independent Qt API for storing passwords securely."
    topics = ("qt", "keychain")
    license = "BSD-3-Clause"
    homepage = "https://github.com/frankosterfeld/qtkeychain"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("topic1", "topic2", "topic3")
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

    def requirements(self):
        self.requires("qt/[>=6.7 <7]", options={"with_dbus": True}, transitive_headers=True, transitive_libs=True)
        self.requires("dbus/1.15.8", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_WITH_QT6"] = True
        # tc.cache_variables["PACKAGE_BUILD_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["qtkeychain"]
