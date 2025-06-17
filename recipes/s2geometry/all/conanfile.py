import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">2.1"


class S2GeometryConan(ConanFile):
    name = "s2geometry"
    description = "Computational geometry and spatial indexing on the sphere"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/s2geometry"
    topics = ("geometry", "spherical-geometry", "spatial-indexing")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        abseil_lower_bound = "20230802.1" if Version(self.version) < "0.12.0" else "20240116.1"
        # tested up to 20250127.0, increase if known to be compatible with newer versions
        self.requires(f"abseil/[>={abseil_lower_bound} <=20250127.0]", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)

    def build_requirements(self):
        if Version(self.version) >= "0.12.0":
            self.tool_requires("cmake/[>=3.18 <4]")

    def validate(self):
        check_min_cppstd(self, 14 if Version(self.version) < "0.12.0" else 17)

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared with Visual Studio")

        abseil_cppstd = self.dependencies.host['abseil'].info.settings.compiler.cppstd
        if abseil_cppstd != self.settings.compiler.cppstd:
            raise ConanInvalidConfiguration(f"s2geometry and abseil must be built with the same compiler.cppstd setting")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GOOGLETEST_ROOT"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["s2"]
        self.cpp_info.set_property("cmake_file_name", "s2")
        self.cpp_info.set_property("cmake_target_name", "s2::s2")
