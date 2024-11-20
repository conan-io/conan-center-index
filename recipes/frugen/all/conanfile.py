from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.1"

class FrugenConan(ConanFile):
    name = "frugen"
    description = "IPMI FRU Information generator / editor tool and library"
    license = ("Apache-2.0", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codeberg.org/IPMITool/frugen"
    topics = ("hardware", "ipmi", "fru")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_json": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_json": True
    }
    implements = ["auto_shared_fpic"]

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("MSVC not supported by the library")

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_json:
            self.requires("json-c/0.18")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIB"] = self.options.shared
        tc.cache_variables["ENABLE_JSON"] = self.options.with_json
        if self.settings.os != "Macos":
            tc.cache_variables["BINARY_STATIC"] = not self.options.shared
        tc.cache_variables["BINARY_32BIT"] = False
        tc.cache_variables["DEBUG_OUTPUT"] = False
        # Dont let CMake find doxygen and try to build documentation
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.components["fru-shared"].libs = ["fru"]
        else:
            self.cpp_info.components["fru-static"].libs = ["fru"]
