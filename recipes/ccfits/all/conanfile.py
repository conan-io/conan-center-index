from conan import ConanFile, conan_version
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class CcfitsConan(ConanFile):
    name = "ccfits"
    description = "CCfits is an object oriented interface to the cfitsio library."
    license = "CFITSIO"
    topics = ("fits", "image", "nasa", "astronomy", "astrophysics", "space")
    homepage = "https://heasarc.gsfc.nasa.gov/fitsio/ccfits"
    url = "https://github.com/conan-io/conan-center-index"
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
        # transitive_headers: CCfits/CCfits.h includes fitsio.h
        self.requires("cfitsio/4.2.0", transitive_headers=True)

    def validate_build(self):
        if Version(self.version) >= "2.6":
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, 11)
        else:
            if conan_version >= "2":
                # FIXME: c3i linter complains, but function is there
                # https://docs.conan.io/2.0/reference/tools/build.html?highlight=check_min_cppstd#conan-tools-build-check-max-cppstd
                import sys
                check_max_cppstd = getattr(sys.modules["conan.tools.build"], "check_max_cppstd")
                # C++17 and higher not supported in ccfits < 2.6 due to auto_ptr
                check_max_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Export symbols for msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "CCfits")
        self.cpp_info.libs = ["CCfits"]
