from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os

required_conan_version = ">=2.0.0"


class LibultrahdrConan(ConanFile):
    name = "libultrahdr"
    description = "libultrahdr is an image format for storing SDR and HDR versions of an image for android."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libultrahdr"
    package_type = "library"
    license = "Apache-2.0"
    topics = ("ultrahdr", "graphics", "image")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
        # libheif support added in 2.0
        "with_libheif": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
        "with_libheif": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if Version(self) < "2.0":
            del self.options.with_libheif

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if Version(self) < "2.0":
            self.options.rm_safe("with_libheif")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.0 <4]")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/[>=4.1.3 <5]")

        if self.options.get_safe("with_libheif", False):
            self.requires("libheif/[>=1.16 <2]")

    def build_requirements(self):
        # The project requires cmake 3.15 but the use of CMAKE_REQUIRE_FIND_PACKAGE_JPEG below
        # requires 3.22.
        self.tool_requires("cmake/[>=3.22 <5]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)

        # Force-disable fallback to internal dependency builder if no deps found
        tc.cache_variables["UHDR_BUILD_DEPS"] = False
        tc.cache_variables['UHDR_BUILD_EXAMPLES'] = False
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_JPEG"] = True
        if is_msvc(self) and not self.options.shared:
            tc.cache_variables["BUILD_FOR_WINUI"] = True

        if Version(self) >= "2.0":
            # Always force activate/deactivate
            tc.cache_variables["UHDR_ENABLE_HEIF"] = self.options.get_safe("with_libheif", False)
            tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_libheif"] = True

        tc.generate()

        deps = CMakeDeps(self)
        if self.options.with_jpeg:
            deps.set_property(self.options.with_jpeg, "cmake_file_name", "JPEG")
            deps.set_property(self.options.with_jpeg, "cmake_target_name", "JPEG::JPEG")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = "-static" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = [f"uhdr{suffix}"]

        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.requires = ["libjpeg::libjpeg"]
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.requires = ["libjpeg-turbo::jpeg"]
        elif self.options.with_jpeg == "mozjpeg":
            self.cpp_info.requires = ["mozjpeg::libjpeg"]

        if self.options.get_safe("with_libheif", False):
            self.cpp_info.requires.append("libheif::libheif")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
