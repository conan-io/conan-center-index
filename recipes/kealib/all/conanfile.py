import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class KealibConan(ConanFile):
    name = "kealib"
    description = "C++ library providing complete access to the KEA image format."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ubarsc/kealib"
    topics = ("image", "raster")

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

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["hdf5"].enable_cxx = True
        self.options["hdf5"].hl = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hdf5/1.14.2", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        hdf5_opts = self.dependencies["hdf5"].options
        if not (hdf5_opts.enable_cxx and hdf5_opts.hl):
            raise ConanInvalidConfiguration("kealib requires hdf5 with cxx and hl enabled.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HDF5_USE_STATIC_LIBRARIES"] = not self.dependencies["hdf5"].options.shared
        tc.cache_variables["HDF5_PREFER_PARALLEL"] = self.dependencies["hdf5"].options.parallel
        tc.cache_variables["LIBKEA_WITH_GDAL"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if is_msvc(self):
            self.cpp_info.libs = ["libkea"]
        else:
            self.cpp_info.libs = ["kea"]
