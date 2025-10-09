from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class ZeroipcConan(ConanFile):
    name = "zeroipc"
    description = "Lock-Free Shared Memory IPC with Codata Structures - A high-performance C++23 header-only library for zero-copy inter-process communication"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/queelius/zeroipc"
    topics = ("shared-memory", "ipc", "lock-free", "codata", "cpp23", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            if Version(self.settings.compiler.cppstd) < "23":
                raise ConanInvalidConfiguration(f"{self.ref} requires C++23")
        
        # Ensure C++23 compiler support
        if self.settings.compiler == "gcc":
            if Version(self.settings.compiler.version) < "13":
                raise ConanInvalidConfiguration(f"{self.ref} requires GCC >= 13 for C++23 support")
        elif self.settings.compiler == "clang":
            if Version(self.settings.compiler.version) < "16":
                raise ConanInvalidConfiguration(f"{self.ref} requires Clang >= 16 for C++23 support")
        elif self.settings.compiler == "msvc":
            if Version(self.settings.compiler.version) < "193":
                raise ConanInvalidConfiguration(f"{self.ref} requires MSVC >= 19.30 (VS 2022) for C++23 support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "cpp", "include"), self.package_folder)
        copy(self, "README.md", self.source_folder, os.path.join(self.package_folder, "share", "zeroipc"))
        copy(self, "SPECIFICATION.md", self.source_folder, os.path.join(self.package_folder, "share", "zeroipc"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        
        # System libraries
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["rt", "pthread"])
        
        # Compiler requirements
        self.cpp_info.cppstd = "23"
        
        # CMake integration
        self.cpp_info.set_property("cmake_file_name", "zeroipc")
        self.cpp_info.set_property("cmake_target_name", "zeroipc::zeroipc")
        self.cpp_info.set_property("cmake_target_aliases", ["zeroipc"])