from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class DevilConan(ConanFile):
    name = "devil"
    description = "Developer's Image Library (DevIL) is a programmer's library to develop applications with very " \
                  "powerful image loading capabilities, yet is easy for a developer to learn and use."
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openil.sourceforge.net/"
    topics = ("devil", "image")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_jasper": [True, False],
        "with_squish": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_jpeg": True,
        "with_tiff": True,
        "with_jasper": True,
        "with_squish": True
    }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder=os.path.join("src", "DevIL"))

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/1.6.44")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_tiff:
            self.requires("libtiff/4.7.0")
        if self.options.with_jasper:
            self.requires("jasper/4.2.4")
        if self.options.with_squish:
            self.requires("libsquish/1.15")

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination="..")

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["IL_NO_PNG"] = not self.options.with_png
        if self.options.with_png:
            tc.variables["IL_PNG_LIB"] = self.dependencies["libpng"].cpp_info.libdirs

        tc.variables["IL_NO_JPG"] = not self.options.with_jpeg
        if self.options.with_jpeg:
            tc.variables["IL_JPEG_LIB"] = self.dependencies["libjpeg"].cpp_info.libdirs

        tc.variables["IL_NO_TIF"] = not self.options.with_tiff
        if self.options.with_tiff:
            tc.variables["IL_TIFF_LIB"] = self.dependencies["libtiff"].cpp_info.libdirs

        tc.variables["IL_NO_JP2"] = not self.options.with_jasper
        if self.options.with_jasper:
            tc.variables["IL_JASPER_LIB"] = self.dependencies["jasper"].cpp_info.libdirs

        tc.variables["IL_USE_DXTC_SQUISH"] = self.options.with_squish
        if self.options.with_squish:
            tc.variables["IL_SQUISH_LIB"] = self.dependencies["libsquish"].cpp_info.libdirs

        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "DevIL")
        self.cpp_info.set_property("cmake_target_name", "DevIL::DevIL")

        self.cpp_info.components["IL"].libs = ["IL"]
        self.cpp_info.components["IL"].set_property("cmake_target_name", "DevIL::IL")
        self.cpp_info.components["IL"].requires = [
            "libpng::libpng",
            "libjpeg::libjpeg",
            "libtiff::libtiff",
            "jasper::jasper",
            "libsquish::libsquish"
        ]
        self.cpp_info.components["ILU"].libs = ["ILU"]
        self.cpp_info.components["ILU"].set_property("cmake_target_name", "DevIL::ILU")
        self.cpp_info.components["ILUT"].libs = ["ILUT"]
        self.cpp_info.components["ILUT"].set_property("cmake_target_name", "DevIL::ILUT")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
