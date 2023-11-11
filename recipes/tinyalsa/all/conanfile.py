from conan import ConanFile
from conan.tools.files import get, export_conandata_patches, apply_conandata_patches, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"

class TinyAlsaConan(ConanFile):
    name = "tinyalsa"
    description = "A small library to interface with ALSA in the Linux kernel"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tinyalsa/tinyalsa"
    topics = ("tiny", "alsa", "sound", "audio", "tinyalsa")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {'shared': False}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only works for Linux.")

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "NOTICE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tinyalsa"]
        self.cpp_info.system_libs.append("dl")
        
        # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f'Appending PATH environment variable: {bin_path}')
        self.env_info.PATH.append(bin_path)
