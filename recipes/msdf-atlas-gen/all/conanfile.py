from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class MsdfAtlasGenConan(ConanFile):
    name = "msdf-atlas-gen"
    license = "MIT"
    homepage = "https://github.com/Chlumsky/msdf-atlas-gen"
    url = "https://github.com/conan-io/conan-center-index"
    description = "MSDF font atlas generator"
    topics = ("msdf-atlas-gen", "msdf", "font", "atlas")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "application"

    def requirements(self):
        self.requires("artery-font-format/1.0")
        self.requires("msdfgen/1.9.1")
        self.requires("lodepng/cci.20200615")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MSDF_ATLAS_GEN_BUILD_STANDALONE"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
