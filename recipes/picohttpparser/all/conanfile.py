from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.layout import basic_layout

required_conan_version = ">=1.51.1"

class PicohttpparserConan(ConanFile):
    name = "picohttpparser"
    description = "tiny HTTP parser written in C (used in HTTP::Parser::XS et al.)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/h2o/picohttpparser"
    topics = ("http", "parser")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
