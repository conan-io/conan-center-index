import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.1"


class SzConan(ConanFile):
    name = "sz"
    description = "SZ3: a modular error-bounded lossy compressor for scientific floating-point data"
    license = "DocumentRef-copyright-and-BSD-license.txt:LicenseRef-SZ3-BSD"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/szcompressor/SZ3"
    topics = ("compression", "lossy-compression", "scientific-data", "hdf5-filter", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_hdf5": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "with_hdf5": False,
        "shared": False,
    }

    def configure(self):
        if self.options.with_hdf5:
            self.package_type = "library"
        else:
            self.options.rm_safe("shared")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Lossless_zstd.hpp declares the Zstd functions it calls, so no Zstd header is needed downstream
        self.requires("zstd/[~1.5]", transitive_libs=True)
        if self.options.with_hdf5:
            # H5Z_SZ3.hpp includes hdf5.h, and its API takes HDF5 handles
            self.requires("hdf5/1.14.6", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        if not self.info.options.with_hdf5:
            self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "tools", "zstd"))
        # use the Conan zstd target instead of find_library(NAMES zstd), which misses zstd_static.lib on MSVC
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "find_library(SZ3_ZSTD_LIBRARY NAMES zstd)",
                        "find_package(zstd REQUIRED CONFIG)\n    set(SZ3_ZSTD_LIBRARY zstd::libzstd)")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_H5Z_FILTER"] = bool(self.options.with_hdf5)
        tc.cache_variables["BUILD_SZ3_BINARY"] = False
        if is_msvc(self):
            # upstream prefers the bundled Zstd under MSVC
            tc.cache_variables["SZ3_USE_BUNDLED_ZSTD"] = False
        tc.cache_variables["H5Z_SZ3_PLUGIN_INSTALL_DIR"] = ""
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_OpenMP"] = True
        tc.cache_variables["CMAKE_SKIP_INSTALL_RPATH"] = True
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "copyright-and-BSD-license.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        CMake(self).install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SZ3")
        self.cpp_info.set_property("cmake_config_version_compat", "SameMajorVersion")

        core = self.cpp_info.components["sz3core"]
        core.set_property("cmake_target_name", "SZ3::SZ3core")
        core.defines = ["SZ3_DEBUG_TIMINGS=0"]
        core.requires = ["zstd::zstd"]
        core.bindirs = []
        core.libdirs = []

        sz3 = self.cpp_info.components["sz3"]
        sz3.set_property("cmake_target_name", "SZ3::SZ3")
        sz3.set_property("cmake_target_aliases", ["SZ3"])
        sz3.requires = ["sz3core"]
        sz3.bindirs = []
        sz3.libdirs = []

        if self.options.with_hdf5:
            h5 = self.cpp_info.components["hdf5sz3"]
            h5.set_property("cmake_target_name", "SZ3::hdf5sz3")
            h5.set_property("cmake_target_aliases", ["hdf5sz3"])
            h5.libs = ["hdf5sz3"]
            h5.includedirs = [os.path.join("include", "hdf5_sz3")]
            h5.requires = ["sz3core", "hdf5::hdf5_c"]
            if self.options.shared:
                plugin_dir = os.path.join(self.package_folder, "bin" if self.settings.os == "Windows" else "lib")
                self.runenv_info.prepend_path("HDF5_PLUGIN_PATH", plugin_dir)
            else:
                h5.defines = ["HDF5SZ3_STATIC"]
