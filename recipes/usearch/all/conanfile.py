import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class USearchConan(ConanFile):
    name = "usearch"
    license = "Apache-2.0"
    description = "Smaller & Faster Single-File Vector Search Engine from Unum"
    homepage = "https://unum-cloud.github.io/usearch/"
    topics = ("search", "vector", "simd", "header-only")
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fp16": [True, False],
        "with_jemalloc": [True, False],
        # "with_openmp": [True, False], # TODO: add after #22353 has been merged
        # "with_simsimd": [True, False], # TODO: add simsimd to CCI
    }
    default_options = {
        "header_only": True,
        "shared": False,
        "fPIC": True,
        "with_fp16": True,
        "with_jemalloc": False,
        # "with_openmp": False,
        # "with_simsimd": False,
    }
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
        }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            del self.options.shared
            self.options.rm_safe("fPIC")
            self.package_type = "header-library"
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def requirements(self):
        if self.options.with_fp16:
            self.requires("fp16/cci.20210320", transitive_headers=True)
        if self.options.with_jemalloc:
            self.requires("jemalloc/5.3.0")
        # if self.options.with_openmp:
        #     self.requires("llvm-openmp/17.0.6")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["CMAKE_PROJECT_usearch_INCLUDE"] = "conan_deps.cmake"
            tc.variables["USEARCH_USE_OPENMP"] = self.options.get_safe("with_openmp", False)
            tc.variables["USEARCH_USE_SIMSIMD"] = self.options.get_safe("with_simsimd", False)
            tc.variables["USEARCH_USE_JEMALLOC"] = self.options.with_jemalloc
            tc.variables["USEARCH_USE_FP16LIB"] = self.options.with_fp16
            tc.variables["USEARCH_INSTALL"] = True
            tc.variables["USEARCH_BUILD_LIB_C"] = True
            tc.variables["USEARCH_BUILD_TEST_CPP"] = False
            tc.variables["USEARCH_BUILD_BENCH_CPP"] = False
            if self.options.with_jemalloc:
                tc.variables["JEMALLOC_ROOT_DIR"] = self.dependencies["jemalloc"].package_folder
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable address sanitizer, which is not compatible with Conan packages
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "-fsanitize=address", "")

    def build(self):
        if not self.options.header_only:
            self._patch_sources()
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
        else:
            copy(self, "*",
                 src=os.path.join(self.source_folder, "include"),
                 dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "usearch")
        self.cpp_info.set_property("cmake_target_name", "usearch::usearch")
        self.cpp_info.set_property("pkg_config_name", "usearch")

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            prefix = "lib" if self.settings.os == "Windows" else ""
            self.cpp_info.libs = [prefix + "usearch_c"]
            if stdcpp_library(self):
                self.cpp_info.system_libs.append(stdcpp_library(self))

        self.cpp_info.defines += [
            f"USEARCH_USE_OPENMP={int(self.options.get_safe('with_openmp', False))}",
            f"USEARCH_USE_FP16LIB={int(bool(self.options.with_fp16))}",
            f"USEARCH_USE_SIMSIMD={int(self.options.get_safe('with_simsimd', False))}",
        ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.append("CoreFoundation")
            self.cpp_info.frameworks.append("Security")
