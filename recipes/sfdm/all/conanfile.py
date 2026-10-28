from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.0.9"


class SfdmConan(ConanFile):
    name = "sfdm"
    description = "simple fast datamatrix decoder"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Jimbopython/sfdm"
    topics = ("image-processing", "barcode-reader", "datamatrix", "barcode-detector," "barcode-decoder")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_test": [True, False],
        "with_zxing_decoder": [True, False],
        "with_libdmtx_decoder": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_test": False,
        "with_zxing_decoder": True,
        "with_libdmtx_decoder": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libdmtx_decoder:
            self.requires("libdmtx/0.7.8")
        if self.options.with_zxing_decoder:
            self.requires("zxing-cpp/2.3.0")

        if self.options.with_test:
            self.requires("catch2/3.11.0")
            self.requires("opencv/4.9.0")

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["sfdm_BUILD_TESTS"] = self.options.with_test
        tc.cache_variables["sfdm_WITH_ZXING_DECODER"] = self.options.with_zxing_decoder
        tc.cache_variables["sfdm_WITH_LIBDMTX_DECODER"] = self.options.with_libdmtx_decoder
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
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
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["sfdm"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
