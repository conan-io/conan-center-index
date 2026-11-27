from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
import os


class Hdf5BloscConan(ConanFile):
    name = "hdf5-blosc2"
    license = "BSD-3-Clause"
    url = "https://github.com/Blosc/HDF5-Blosc2"
    description = "Blosc2 compression filter for HDF5"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "CMakeDeps"
    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("hdf5/[>=2 <3]")
        self.requires("c-blosc2/[>=3.1.2 <4]", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination="upstream_src", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HDF5_BLOSC2_SRC_DIR"] = os.path.join(
            self.source_folder, "upstream_src").replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        src = os.path.join(self.source_folder, "upstream_src")
        copy(self, "LICENSE.txt", src, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(src, "LICENSES"), os.path.join(self.package_folder, "licenses"))
        CMake(self).install()

    def package_info(self):
        self.cpp_info.libs = ["blosc2_filter"]
        self.cpp_info.set_property("cmake_file_name", "hdf5-blosc2")
        self.cpp_info.set_property("cmake_target_name", "hdf5-blosc2::hdf5-blosc2")