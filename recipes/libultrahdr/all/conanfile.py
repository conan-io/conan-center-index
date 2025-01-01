from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibultrahdrConan(ConanFile):
    name = "libultrahdr"
    description = "libultrahdr is an image format for storing SDR and HDR versions of an image for android."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libultrahdr"
    license = "Apache-2.0"
    topics = ("ultrahdr", "graphics", "image")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.3")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["UHDR_BUILD_DEPS"] = False
        if self.options.with_jpeg == "libjpeg":
            tc.variables["CONAN_USE_JPEG"] = True
        elif self.options.with_jpeg == "libjpeg-turbo":
            tc.variables["CONAN_USE_JPEGTURBO"] = True
        elif self.options.with_jpeg == "mozjpeg":
            tc.variables["CONAN_USE_MOZJPEG"] = True

        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # if self.options.shared:
        #     rm(self, "*[!.dll]", os.path.join(self.package_folder, "bin"))
        # else:
        #     rmdir(self, os.path.join(self.package_folder, "bin"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "libpng"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "share"))
        # rm(self, "*.cmake", os.path.join(self.package_folder, "lib", "cmake", "PNG"))

    def package_info(self):
        self.cpp_info.libs = ['uhdr']

        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.requires = ["libjpeg::libjpeg"]
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.requires = ["libjpeg-turbo::jpeg"]
        elif self.options.with_jpeg == "mozjpeg":
            self.cpp_info.requires = ["mozjpeg::libjpeg"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
