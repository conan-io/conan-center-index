import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir, rm, replace_in_file, apply_conandata_patches, export_conandata_patches
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.21"

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
        self.requires("libjpeg/9f", transitive_headers=True)
        if self.options.with_lcms:
            self.requires("lcms/[>=2.14 <3]", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Remove the pre-existing config.h file to allow CMake to generate its own
        rm(self, "config.h", self.source_folder)
        apply_conandata_patches(self)

    def export_sources(self):
        export_conandata_patches(self)

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
        tc.variables["MNG_INSTALL_LIB_DIR"] = "lib"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake_lists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmake_lists, "CMAKE_MINIMUM_REQUIRED(VERSION 2.6)", "CMAKE_MINIMUM_REQUIRED(VERSION 3.5)")
        replace_in_file(self, cmake_lists, "${JPEG_LIBRARY}", "${JPEG_LIBRARIES}")
        replace_in_file(self, cmake_lists, "${ZLIB_LIBRARY}", "${ZLIB_LIBRARIES}")
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
        self.cpp_info.set_property("cmake_file_name", "mng")
        self.cpp_info.set_property("cmake_target_name", "MNG::MNG")

        if self.settings.os == "Windows" and self.options.shared:
            lib_name = "mng"
            self.cpp_info.defines.append("MNG_USE_DLL")
        elif self.settings.compiler == "msvc":
            lib_name = "libmng"
        else:
            lib_name = "mng"
        self.cpp_info.libs = [lib_name]
        self.cpp_info.requires = ["zlib::zlib", "libjpeg::libjpeg"]

        if self.options.with_lcms:
            self.cpp_info.requires.append("lcms::lcms")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
