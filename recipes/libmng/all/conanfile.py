import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir, rm
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.53.0"

class LibmngConan(ConanFile):
    name = "libmng"
    license = "libmng"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/libmng/"
    description = "Multiple-image Network Graphics library."
    topics = ("mng", "png", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lcms": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lcms": True,
    }
    package_type = "library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]", transitive_headers=True)
        self.requires("libjpeg/9e", transitive_headers=True)
        if self.options.with_lcms:
            self.requires("lcms/2.14", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Remove the pre-existing config.h file to allow CMake to generate its own
        rm(self, "config.h", self.source_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["WITH_LCMS2"] = self.options.with_lcms
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # Set properties on the main cpp_info
        self.cpp_info.set_property("cmake_file_name", "mng")
        self.cpp_info.set_property("cmake_target_name", "MNG::MNG")

        lib_name = "libmng" if self.settings.compiler == "msvc" else "mng"
        self.cpp_info.libs = [lib_name]
        self.cpp_info.requires = ["zlib::zlib", "libjpeg::libjpeg"]

        if self.options.with_lcms:
            self.cpp_info.requires.append("lcms::lcms")

        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")
