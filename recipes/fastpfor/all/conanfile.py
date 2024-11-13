from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.53.0"

class FastPFORConan(ConanFile):
    name = "fastpfor"
    description = "Fast integer compression"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/FastPFor"
    topics = ("compression", "sorted-lists", "simd", "x86", "x86-64")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if str(self.settings.arch).startswith("armv8"):
            self.requires("simde/0.8.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_TEST"] = False
        if str(self.settings.arch).startswith("armv8"):
            tc.cache_variables["SUPPORT_NEON"] = True
            tc.preprocessor_definitions["SIMDE_ENABLE_NATIVE_ALIASES"] = 1
            if is_apple_os(self):
                tc.variables["CMAKE_OSX_ARCHITECTURES"] = {
                    "armv8": "arm64",
                }.get(str(self.settings.arch), str(self.settings.arch))
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["FastPFOR"]

        self.cpp_info.set_property("cmake_file_name", "FastPFOR")
        self.cpp_info.set_property("cmake_target_name", "FastPFOR::FastPFOR")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if str(self.settings.arch).startswith("armv8"):
            self.cpp_info.defines = ["SIMDE_ENABLE_NATIVE_ALIASES"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "FastPFOR"
        self.cpp_info.filenames["cmake_find_package_multi"] = "FastPFOR"
        self.cpp_info.names["cmake_find_package"] = "FastPFOR"
        self.cpp_info.names["cmake_find_package_multi"] = "FastPFOR"
