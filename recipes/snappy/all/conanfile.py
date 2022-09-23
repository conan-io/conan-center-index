from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class SnappyConan(ConanFile):
    name = "snappy"
    description = "A fast compressor/decompressor"
    topics = ("snappy", "google", "compressor", "decompressor")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/snappy"
    license = "BSD-3-Clause"

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SNAPPY_BUILD_TESTS"] = False
        if Version(self.version) >= "1.1.8":
            tc.variables["SNAPPY_FUZZING_BUILD"] = False
            tc.variables["SNAPPY_REQUIRE_AVX"] = False
            tc.variables["SNAPPY_REQUIRE_AVX2"] = False
            tc.variables["SNAPPY_INSTALL"] = True
        if Version(self.version) >= "1.1.9":
            tc.variables["SNAPPY_BUILD_BENCHMARKS"] = False
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Snappy")
        self.cpp_info.set_property("cmake_target_name", "Snappy::snappy")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["snappylib"].libs = ["snappy"]
        if not self.options.shared:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["snappylib"].system_libs.append(libcxx)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Snappy"
        self.cpp_info.names["cmake_find_package_multi"] = "Snappy"
        self.cpp_info.components["snappylib"].names["cmake_find_package"] = "snappy"
        self.cpp_info.components["snappylib"].names["cmake_find_package_multi"] = "snappy"
        self.cpp_info.components["snappylib"].set_property("cmake_target_name", "Snappy::snappy")
