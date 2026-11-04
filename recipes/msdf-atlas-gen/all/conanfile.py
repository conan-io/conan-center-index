import os

from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class MsdfAtlasGenConan(ConanFile):
    name = "msdf-atlas-gen"
    description = "MSDF font atlas generator"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Chlumsky/msdf-atlas-gen"
    topics = ("msdf-atlas-gen", "msdf", "font", "atlas")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def requirements(self):
        if Version(self.version) < "1.3":
            self.requires("msdfgen/1.9.1")
            self.requires("artery-font-format/1.0")
            self.requires("lodepng/cci.20200615")
        else:
            self.requires("msdfgen/1.12")
            self.requires("artery-font-format/1.1")
            self.requires("libpng/[>=1.6 <2]")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MSDF_ATLAS_GEN_BUILD_STANDALONE"] = True
        tc.cache_variables["MSDF_ATLAS_USE_VCPKG"] = False
        tc.cache_variables["MSDF_ATLAS_USE_SKIA"] = False
        tc.cache_variables["MSDF_ATLAS_NO_ARTERY_FONT"] = False
        tc.cache_variables["MSDF_ATLAS_MSDFGEN_EXTERNAL"] = True
        tc.cache_variables["MSDF_ATLAS_INSTALL"] = True
        if Version(self.version) >= "1.3":
            tc.preprocessor_definitions["MSDFGEN_USE_LIBPNG"] = 1
        if is_msvc(self):
            tc.cache_variables["MSDF_ATLAS_DYNAMIC_RUNTIME"] = "dynamic" in str(self.settings.compiler.runtime) or "MD" in str(self.settings.compiler.runtime)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
