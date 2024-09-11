from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, copy, get, replace_in_file, rename
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if is_msvc(self):
            del self.options.shared
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        # FIXME: Windows supported: https://github.com/kosma/minmea?tab=readme-ov-file#compatibility
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on Visual Studio and msvc. Contributions are welcome.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        #if is_msvc(self):
        #    tc.preprocessor_definitions["MINMEA_INCLUDE_COMPAT"] = "1"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # INFO: Disable pkg-config searching for the test library libcheck
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                         "pkg_check_modules",
                         "# pkg_check_modules")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="minmea")

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "libminmea.a", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "libminmea.so", self.build_folder, os.path.join(self.package_folder, "lib"))
        copy(self, "libminmea.dylib", self.build_folder, os.path.join(self.package_folder, "lib"))
        if self.settings.os == "Windows":
            copy(self, "minmea.lib", self.build_folder, os.path.join(self.package_folder, "lib"))
            # INFO: https://github.com/kosma/minmea?tab=readme-ov-file#compatibility Need to rename the file
            rename(self, os.path.join(self.package_folder, "include", "minmea_compat_windows.h"),
                    os.path.join(self.package_folder, "include", "minmea_compat.h"))

    def package_info(self):
        self.cpp_info.libs = ["minmea"]
        if is_msvc(self):
            self.cpp_info.defines.append("MINMEA_INCLUDE_COMPAT")
