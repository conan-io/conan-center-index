from conan import ConanFile
from conan.tools.files import get, rmdir, save, load
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"

class TinyEXIFConan(ConanFile):
    name = "tinyexif"
    description = "Tiny ISO-compliant C++ EXIF and XMP parsing library for JPEG"
    license = "BSD 2-Clause"
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

    @property
    def _min_cppstd(self):
        return 11

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

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["LINK_CRT_STATIC_LIBS"] = is_msvc_static_runtime(self)
        tc.variables["BUILD_DEMO"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        filename = os.path.join(self.source_folder, self.source_folder, "TinyEXIF.h")
        file_content = load(save, filename)
        license_start = "/*"
        license_end = "*/"
        license_contents = file_content[file_content.find(license_start)+len(license_start):file_content.find(license_end)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        libpostfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"TinyEXIF{libpostfix}"]

        self.cpp_info.set_property("cmake_file_name", "TinyEXIF")
        self.cpp_info.set_property("cmake_target_name", "TinyEXIF::TinyEXIF")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "TinyEXIF"
        self.cpp_info.filenames["cmake_find_package_multi"] = "TinyEXIF"
        self.cpp_info.names["cmake_find_package"] = "TinyEXIF"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyEXIF"
