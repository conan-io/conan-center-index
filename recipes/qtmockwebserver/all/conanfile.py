from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get, export_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMake, CMakeToolchain
import os

class QtMockWebServerConan(ConanFile):
    name = "qtmockwebserver"
    license = "Apache-2.0"
    url = "https://github.com/ArchangelSDY/QtMockWebServer"
    description = "A simple mock web server built on top of Qt."
    topics = ("Qt", "mock", "webserver")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    requires = "qt/[>=5.9 <7]"
    generators = "CMakeDeps", "CMakeToolchain"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include/qtmockwebserver", src="src", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["qtmockwebserver"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
