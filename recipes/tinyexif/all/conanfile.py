import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rmdir, replace_in_file, copy
from conan.tools.microsoft import is_msvc_static_runtime

required_conan_version = ">=2"

class TinyEXIFConan(ConanFile):
    name = "tinyexif"
    description = "Tiny ISO-compliant C++ EXIF and XMP parsing library for JPEG"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cdcseacave/TinyEXIF/"
    topics = ("exif", "exif-metadata", "exif-ata-extraction", "exif-reader", "xmp", "xmp-parsing-library")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tinyxml2/9.0.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 11)",
                        "## set(CMAKE_CXX_STANDARD 11)")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["LINK_CRT_STATIC_LIBS"] = is_msvc_static_runtime(self)
        tc.cache_variables["BUILD_DEMO"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        libpostfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"TinyEXIF{libpostfix}"]

        self.cpp_info.set_property("cmake_file_name", "TinyEXIF")
        self.cpp_info.set_property("cmake_target_name", "TinyEXIF::TinyEXIF")
