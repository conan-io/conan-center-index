from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
import os

required_conan_version = ">=2.1"


class Openfx(ConanFile):
    name = "openfx"
    license = "BSD-3-Clause"
    description = "OpenFX image processing plug-in standard"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AcademySoftwareFoundation/openfx"
    topics = ("graphics", "vfx", "image-processing", "plugins")
    package_type = "static-library"

    options = {
        "fPIC": [True, False],
    }

    settings = "os", "arch", "compiler", "build_type"
    default_options = {
        "fPIC": True,
        # "expat/*:shared": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        # Symbols used in public headers
        self.requires("expat/[>=2.6.2 <3]", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "OpenFX", "OpenFX.cmake")])

        self.cpp_info.components["Api"].includedirs = ["include"]
        self.cpp_info.components["HostSupport"].libs = ["OfxHost"]
        self.cpp_info.components["HostSupport"].includedirs = [os.path.join("include", "HostSupport")]
        self.cpp_info.components["HostSupport"].requires = ["Api", "expat::expat"]
        self.cpp_info.components["Support"].libs = ["OfxSupport"]
        self.cpp_info.components["Support"].includedirs = [os.path.join("include", "Support")]
        self.cpp_info.components["Support"].requires = ["Api"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["HostSupport"].system_libs = ["dl"]
