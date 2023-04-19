from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake
import os


required_conan_version = ">=1.53.0"


class B64Conan(ConanFile):
    name = "b64"
    description = "A library of ANSI C routines for fast encoding/decoding data into and from a base64-encoded format."
    license = "CC0-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libb64.sourceforge.net/"
    topics = ("base64", "codec", "encoder", "decoder")
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["b64"]

        # TODO: Only for Conan 1.x legacy - Remove after running Conan 2.x only
        self.env_info.PATH = os.path.join(self.package_folder, "bin")
