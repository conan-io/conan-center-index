from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
import os

required_conan_version = ">=2"


class VectorscanConan(ConanFile):
    name = "vectorscan"
    description = "A portable fork of the high-performance regular expression matching library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/VectorCamp/vectorscan"
    topics = ("regex", "regular expressions", "hyperscan")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "debug_output": [True, False],
        "dump_support": [True, False, "auto"],
        "with_cpu_native": [True, False],
        "with_fat_runtime": [True, False],
        "with_avx": [False, "avx2", "avx512", "avx512vbmi"],
        "with_sve": [False, "sve", "sve2", "sve2_bitperm"],
        "with_chimera": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debug_output": False,
        "dump_support": "auto",
        "with_cpu_native": False,
        "with_fat_runtime": False,
        "with_avx": False,
        "with_sve": False,
        "with_chimera": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_fat_runtime
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.with_avx
        if str(self.settings.arch).startswith("arm"):
            del self.options.with_sve

    def configure(self):
        if self.options.shared or self.options.with_cpu_native:
            self.options.rm_safe("fPIC")
        if self.options.with_cpu_native:
            self.options.rm_safe("with_fat_runtime")
        if self.options.get_safe("with_fat_runtime"):
            self.options.rm_safe("with_avx")
            self.options.rm_safe("with_sve")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.86.0")
        self.requires("simde/0.8.2")
        if self.options.with_chimera:
            self.requires("pcre/8.45")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.shared and self.options.with_chimera:
            raise ConanInvalidConfiguration("Chimera build requires static building")
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("MSVC is not supported by upstream build scripts")

    def validate_build(self):
        if self.settings.os == "Macos" and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building is not supported on macOS")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18.4 <4]")
        self.tool_requires("ragel/6.10")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["DEBUG_OUTPUT"] = self.options.debug_output
        if self.options.dump_support != "auto":
            tc.variables["DUMP_SUPPORT"] = self.options.dump_support
        if "with_cpu_native" in self.options:
            tc.variables["WITH_CPU_NATIVE"] = self.options.with_cpu_native
        if "with_fat_runtime" in self.options:
            tc.variables["WITH_FAT_RUNTIME"] = self.options.with_fat_runtime
        if "with_avx" in self.options:
            if not self.options.with_avx:
                tc.cache_variables["BUILD_AVX2"] = False
            elif self.options.with_avx == "avx2":
                tc.cache_variables["BUILD_AVX2"] = True
            elif self.options.with_avx == "avx512":
                tc.variables["BUILD_AVX512"] = True
            elif self.options.with_avx == "avx512vbmi":
                tc.variables["BUILD_AVX512VBMI"] = True
        if "with_sve" in self.options:
            if not self.options.with_sve:
                tc.cache_variables["BUILD_SVE"] = False
            elif self.options.with_sve == "sve":
                tc.cache_variables["BUILD_SVE"] = True
            elif self.options.with_sve == "sve2":
                tc.cache_variables["BUILD_SVE2"] = True
            elif self.options.with_sve == "sve2_bitperm":
                tc.cache_variables["BUILD_SVE2_BITPERM"] = True
        tc.cache_variables["BUILD_CHIMERA"] = self.options.with_chimera
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
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
        hs_include_dir = os.path.join("include", "hs")
        self.cpp_info.components["hs"].set_property("pkg_config_name", "libhs")
        self.cpp_info.components["hs"].set_property("cmake_target_name", "hs")
        self.cpp_info.components["hs"].libs = ["hs"]
        self.cpp_info.components["hs"].requires = ["boost::headers", "simde::simde"]
        self.cpp_info.components["hs"].includedirs = [hs_include_dir]

        self.cpp_info.components["hs_runtime"].libs = ["hs_runtime"]
        self.cpp_info.components["hs_runtime"].includedirs = [hs_include_dir]

        if self.options.with_chimera:
            self.cpp_info.components["chimera"].set_property("pkg_config_name", "libch")
            self.cpp_info.components["chimera"].set_property("cmake_target_name", "chimera")
            self.cpp_info.components["chimera"].libs = ["chimera"]
            self.cpp_info.components["chimera"].requires = ["pcre::libpcre", "hs"]
            self.cpp_info.components["chimera"].includedirs = [hs_include_dir]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["hs"].system_libs = ["m"]
            self.cpp_info.components["hs_runtime"].system_libs = ["m"]

            if self.options.with_chimera:
                self.cpp_info.components["chimera"].system_libs = ["m"]
