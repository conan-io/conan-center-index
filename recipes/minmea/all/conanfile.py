from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"

class MinmeaConan(ConanFile):
    name = "minmea"
    description = "a lightweight GPS NMEA 0183 parser library in pure C"
    license = ("WTFPL", "MIT", "LGPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kosma/minmea"
    topics = ("gps", "NMEA", "parser")
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        # INFO: Windows mingw supported: https://github.com/kosma/minmea?tab=readme-ov-file#compatibility
        # INFO: MSVC fails with error C2011: 'timespec': 'struct' type redefinition
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on Visual Studio and msvc. Use mingw instead or similar.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["MINMEA_INCLUDE_COMPAT"] = "1"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="minmea")

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "minmea.h", self.source_folder, os.path.join(self.package_folder, "include"))
        copy(self, "libminmea.a", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "libminmea.so", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "libminmea.dylib", self.build_folder, os.path.join(self.package_folder, "lib"))
        if self.settings.os == "Windows":
            copy(self, "libminmea.dll.a", self.build_folder, os.path.join(self.package_folder, "lib"))
            copy(self, "libminmea.dll", self.build_folder, os.path.join(self.package_folder, "bin"))
            copy(self, "minmea_compat.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["minmea"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["MINMEA_INCLUDE_COMPAT=1"]
