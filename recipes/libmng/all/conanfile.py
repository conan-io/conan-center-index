import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
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
        "with_jpeg": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lcms": True,
        "with_jpeg": True,
    }
    package_type = "library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_lcms:
            self.requires("lcms/2.14")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        tc.variables["WITH_JPEG"] = self.options.with_jpeg
        tc.generate()

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
        self.cpp_info.set_property("cmake_file_name", "mng")
        self.cpp_info.set_property("cmake_target_name", "MNG::MNG")
        self.cpp_info.libs = ["mng"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: Remove after Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "MNG"
        self.cpp_info.names["cmake_find_package_multi"] = "MNG"
