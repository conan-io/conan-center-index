from conan import ConanFile, conan_version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class AlacConan(ConanFile):
    name = "alac"
    description = "The Apple Lossless Audio Codec (ALAC) is a lossless audio " \
                  "codec developed by Apple and deployed on all of its platforms and devices."
    license = "Apache-2.0"
    topics = ("alac", "audio-codec")
    homepage = "https://macosforge.github.io/alac"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utility": True,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ALAC_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["ALAC_BUILD_UTILITY"] = self.options.utility
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["alac"]

        if Version(conan_version).major < 2 and self.options.utility:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
