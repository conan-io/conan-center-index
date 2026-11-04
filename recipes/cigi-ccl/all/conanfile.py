from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.53.0"

class CigiClConan(ConanFile):
    name = "cigi-ccl"
    description = "Industry standard communication with compliant image generators"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cigi.sourceforge.io/product_ccl.php"
    topics = ("simulation", "interface engines", "data visualization")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_apple_os(self):
            # CigiOutgoingMsg.cpp:196:38: error: use of undeclared identifier 'PTHREAD_MUTEX_RECURSIVE_NP'
            raise ConanInvalidConfiguration(f"{self.settings.os} Conan recipe is not supported on Apple. Contributions are welcome.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

        tc.generate()

    def _patch_sources(self):
        cmake_lists_fixes = {
            # This old CMakeLists.txt had PROJECT() before CMAKE_MINIMUM_REQUIRED(); this order must be inverted
            "CMAKE_MINIMUM_REQUIRED(VERSION 2.4.7)": "",
            "PROJECT(ccl)": "CMAKE_MINIMUM_REQUIRED(VERSION 2.4.7)\nPROJECT(ccl)",
            # Using backslash for path is being interpreted as invalid escape sequence in newer versions of CMake
            "Header Files\\": "Header Files/",
            "Source Files\\": "Source Files/",
            # Incorrectly tries to install both the static and shared targets
            "INSTALL(TARGETS cigicl-static cigicl-shared": f"INSTALL(TARGETS {'cigicl-shared' if self.options.shared else 'cigicl-static'}"
        }

        for old, new in cmake_lists_fixes.items():
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), old, new)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        if self.options.shared:
            cmake.build(target="cigicl-shared")
        else:
            cmake.build(target="cigicl-static")

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "license.html", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "cigicl")
        build_type_suffix = ""
        if self.settings.build_type == "Debug" and self.settings.os == "Windows":
            build_type_suffix = "D"

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])

        if self.options.shared:
            self.cpp_info.libs = ["ccl_dll" + build_type_suffix]
            self.cpp_info.defines = ["CCL_DLL"]
        else:
            self.cpp_info.libs = ["ccl_lib" + build_type_suffix]
