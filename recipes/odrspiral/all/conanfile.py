from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2"

class odrSpiralConan(ConanFile):
    name="odrspiral"
    description="Euler spirals as used for clothoids in OpenDRIVE"
    license="BSD-2-Clause license"
    url="https://github.com/DLR-TS/odrSpiral"
    homepage="https://github.com/DLR-TS/odrSpiral"
    topics="Euler spirals, clothoids, OpenDRIVE"
    package_type="library"
    settings="os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "*", os.path.join(self.source_folder, "lib"), os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # Conan automatically sets libdirs=["lib"] and includedirs=["include"] by default
        # and infers other traits based on package_type
        self.cpp_info.libs = collect_libs(self)    
