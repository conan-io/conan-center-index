import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.54.0"


class PackageConan(ConanFile):
    name = "libecwj2"
    description = "Legacy version of the ERDAS ECW/JP2 SDK. Provides support for the ECW (Enhanced Compressed Wavelet) and the JPEG 2000 image formats."
    license = "DocumentRef-License.txt:LicenseRef-libecwj2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://trac.osgeo.org/gdal/wiki/ECW"
    topics = ("image", "ecw", "jp2", "jpeg2000")

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
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src", "Source"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libjpeg/9e", transitive_headers=True, transitive_libs=True)
        self.requires("tinyxml/2.6.2", transitive_headers=True, transitive_libs=True)
        # self.requires("lcms/2.14")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 98)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "Source"))
        cmake.build()

    def package(self):
        copy(self, "License.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libecwj2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "rt", "m", "pthread"])
        if stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
