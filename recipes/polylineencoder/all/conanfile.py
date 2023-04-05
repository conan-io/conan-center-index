from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class PolylineencoderConan(ConanFile):
    name = "polylineencoder"
    description = "Google Encoded Polyline Algorithm Format library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vahancho/polylineencoder"
    topics = ("gepaf", "encoded-polyline", "google-polyline")
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
        if Version(self.version) >= "1.1.1":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if Version(self.version) >= "1.1.1":
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = "ON"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if Version(self.version) < "1.1.1":
            self.cpp_info.libs = ["polylineencoder"]
            if self.settings.os in ["Linux", "FreeBSD"] and self.options.shared:
                self.cpp_info.system_libs.append("m")
        else:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
