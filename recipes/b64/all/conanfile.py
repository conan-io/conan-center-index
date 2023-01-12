from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class B64Conan(ConanFile):
    name = "b64"
    description = "A library of ANSI C routines for fast encoding/decoding data into and from a base64-encoded format."
    license = "CC0-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libb64.sourceforge.net/"
    topics = ("base64", "codec", "encoder", "decoder")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "static": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "static": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"))

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["b64"]
