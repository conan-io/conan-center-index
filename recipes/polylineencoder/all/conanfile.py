from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def package_id(self):
        if Version(self.version) >= "1.1.2":
            self.info.clear()

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_TESTING"] = False
        if self.settings.os == "Windows" and self.options.shared:
            toolchain.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = "ON"
        toolchain.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
        if Version(self.version) == "1.0.0":
            self.cpp_info.libs.append("polylineencoder")
            if self.settings.os in ["Linux", "FreeBSD"] and self.options.shared:
                self.cpp_info.system_libs.append("m")
