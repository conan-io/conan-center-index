import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get

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

    def export_sources(self):
        export_conandata_patches(self)

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
        self.requires("hdf5/1.14.1", transitive_headers=True)

    def validate(self):
        hdf5_opts = self.dependencies["hdf5"].options
        if not (hdf5_opts.enable_cxx and hdf5_opts.hl):
            raise ConanInvalidConfiguration("kealib requires hdf5 with cxx and hl enabled.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HDF5_USE_STATIC_LIBRARIES"] = not self.dependencies["hdf5"].options.shared
        tc.variables["HDF5_PREFER_PARALLEL"] = self.dependencies["hdf5"].options.parallel
        tc.variables["LIBKEA_WITH_GDAL"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["kea"]
