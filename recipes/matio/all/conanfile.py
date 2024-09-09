import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class MatioConan(ConanFile):
    name = "matio"
    description = "Matio is a C library for reading and writing binary MATLAB MAT files."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/matio/"
    topics = ("matlab", "mat-file", "file-format", "hdf5")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "extended_sparse": [True, False],
        "mat73": [True, False],
        "with_hdf5": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "extended_sparse": True,
        "mat73": True,
        "with_hdf5": True,
        "with_zlib": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.3")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if not self.options.with_hdf5 and self.options.mat73:
            raise ConanInvalidConfiguration("Support of version 7.3 MAT files requires HDF5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MATIO_ENABLE_CPPCHECK"] = False
        tc.variables["MATIO_EXTENDED_SPARSE"] = self.options.extended_sparse
        tc.variables["MATIO_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["MATIO_SHARED"] = self.options.shared
        tc.variables["MATIO_MAT73"] = self.options.mat73
        tc.variables["MATIO_WITH_HDF5"] = self.options.with_hdf5
        tc.variables["MATIO_WITH_ZLIB"] = self.options.with_zlib
        tc.variables["HDF5_USE_STATIC_LIBRARIES"] = (
            self.options.with_hdf5 and not self.dependencies["hdf5"].options.shared
        )
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if is_msvc(self):
            self.cpp_info.libs = ["libmatio"]
        else:
            self.cpp_info.libs = ["matio"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        # TODO: remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
