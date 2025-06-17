from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"

class CrossDBConan(ConanFile):
    name = "crossdb"
    description = "Ultra High-performance Lightweight Embedded and Server OLTP RDBMS"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/crossdb-org/crossdb"
    topics = ("database", "oltp", "embedded")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"${self.ref} does not support MSVC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "0.11.0": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["crossdb"]

        if Version(self.version) >= "0.10.0" and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
