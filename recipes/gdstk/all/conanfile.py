from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import collect_libs, export_conandata_patches, apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
from conan.tools.env import VirtualRunEnv
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"

class GdstkConan(ConanFile):
    name = "gdstk"
    description = "gdstk"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/heitzmann/gdstk"
    topics = ("gdsii", "oasii", "gdstk", "2d")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "max_devices": [1,2,3,4],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "max_devices" : 1,
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

    def requirements(self):
        self.requires("zlib/1.3.1")
        self.requires("qhull/8.0.2")
        self.requires("clipper/6.4.2")


    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)
 
    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = False
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["VSG_SUPPORTS_ShaderCompiler"] = 0
        tc.variables["VSG_MAX_DEVICES"] = self.options.max_devices
        tc.generate()

        deps = CMakeDeps(self)

        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        self.cpp_info.set_property("cmake_file_name", "gdstk")
        self.cpp_info.set_property("cmake_target_name", "gdstk::gdstk")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
