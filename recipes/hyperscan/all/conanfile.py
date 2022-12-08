from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class HyperscanConan(ConanFile):
    name = "hyperscan"
    description = "High-performance regular expression matching library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.hyperscan.io"
    topics = ("regex", "regular expressions")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "optimise": [True, False, "auto"],
        "debug_output": [True, False, "auto"],
        "build_avx512": [True, False],
        "fat_runtime": [True, False],
        "build_chimera": [True, False],
        "dump_support": [True, False, "auto"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "optimise": "auto",
        "debug_output": "auto",
        "build_avx512": False,
        "fat_runtime": False,
        "build_chimera": False,
        "dump_support": "auto",
    }

    @property
    def _min_cppstd(self):
        return 11

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
        self.requires("boost/1.80.0");
        if self.options.build_chimera:
            self.requires("pcre/8.45")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if self.options.shared and self.options.build_chimera:
            raise ConanInvalidConfiguration("Chimera build requires static building")

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("Hyperscan only support x86 architecture")

    def build_requirements(self):
        self.build_requires("ragel/6.10");

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.optimise != "auto":
            tc.variables["OPTIMISE"] = self.options.optimise
        if self.options.debug_output != "auto":
            tc.variables["DEBUG_OUTPUT"] = self.options.debug_output
        tc.variables["BUILD_AVX512"] = self.options.build_avx512
        tc.variables["FAT_RUNTIME"] = self.options.fat_runtime
        tc.variables["BUILD_CHIMERA"] = self.options.build_chimera
        if self.options.dump_support != "auto":
            tc.variables["DUMP_SUPPORT"] = self.options.dump_support
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "hyperscan"
        self.cpp_info.names["cmake_find_package_multi"] = "hyperscan"

        self.cpp_info.components["hs"].libs = ["hs"]
        self.cpp_info.components["hs"].requires = ["boost::headers"]
        self.cpp_info.components["hs"].names["cmake_find_package"] = "hs"
        self.cpp_info.components["hs"].names["cmake_find_package_multi"] = "hs"
        self.cpp_info.components["hs"].set_property("cmake_target_name", "hyperscan::hs")
        self.cpp_info.components["hs"].set_property("pkg_config_name", "libhs")


        self.cpp_info.components["hs_runtime"].libs = ["hs_runtime"]
        self.cpp_info.components["hs_runtime"].names["cmake_find_package"] = "hs_runtime"
        self.cpp_info.components["hs_runtime"].names["cmake_find_package_multi"] = "hs_runtime"
        self.cpp_info.components["hs_runtime"].set_property("cmake_target_name", "hyperscan::hs_runtime")
        self.cpp_info.components["hs_runtime"].set_property("pkg_config_name", "libhs_runtime")


        if self.options.build_chimera:
            self.cpp_info.components["chimera"].libs = ["chimera"]
            self.cpp_info.components["chimera"].requires = ["pcre::libpcre", "hs"]
            self.cpp_info.components["chimera"].names["cmake_find_package"] = "chimera"
            self.cpp_info.components["chimera"].names["cmake_find_package_multi"] = "chimera"
            self.cpp_info.components["chimera"].set_property("cmake_target_name", "hyperscan::chimera")
            self.cpp_info.components["chimera"].set_property("pkg_config_name", "libchimera")

        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["hs"].system_libs = ["m"]
                self.cpp_info.components["hs_runtime"].system_libs = ["m"]

                if self.options.build_chimera:
                    self.cpp_info.components["chimera"].system_libs = ["m"]

