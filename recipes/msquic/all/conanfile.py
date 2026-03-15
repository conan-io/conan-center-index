from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, rmdir
from conan.tools.scm import Git
import os


class MsQuicConan(ConanFile):
    name = "msquic"
    package_type = "library"

    # Metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, C implementation of the IETF QUIC protocol"
    homepage = "https://github.com/microsoft/msquic"
    topics = ("quic", "networking", "protocol", "microsoft", "ietf")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    implements = ["auto_shared_fpic"]

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/microsoft/msquic.git", target=".")
        git.checkout(commit=f"v{self.version}")
        git.run("submodule update --init --recursive")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QUIC_BUILD_TOOLS"] = False
        tc.variables["QUIC_BUILD_TEST"] = False
        tc.variables["QUIC_BUILD_PERF"] = False
        if self.options.shared:
            tc.variables["BUILD_SHARED_LIBS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "msquic")
        self.cpp_info.set_property("cmake_target_name", "msquic::msquic")
        self.cpp_info.libs = ["msquic"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Security"]
