import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import  copy, get, replace_in_file, rmdir
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.57.0"


class RuyConan(ConanFile):
    name = "ruy"
    description = "ruy is a matrix multiplication library.\n" \
                  "Its focus is to cover the matrix multiplication needs of neural network inference engines\n"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/ruy"
    license = "Apache-2.0"
    topics = ("matrix", "multiplication", "neural", "network", "AI", "tensorflow")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191", 
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning("Compiler is unknown. Assuming it supports C++14.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("Build requires support for C++14. Minimum version for {} is {}"
                .format(str(self.settings.compiler), minimum_version))

        if str(self.settings.compiler) == "clang" and Version(self.settings.compiler.version) <= 5 and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration("Debug builds are not supported on older versions of Clang (<=5)")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("cpuinfo/cci.20220228")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["RUY_MINIMAL_BUILD"] = True
        tc.cache_variables["RUY_FIND_CPUINFO"] = True
        # Ruy public headers don't have API decorators,
        # export everything to support shared libraries on Windows
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        patches = {
            #Remove the invocation after project(), see https://github.com/google/ruy/issues/328
            "cmake_minimum_required(VERSION 3.13)": "",
            # Ensure `cmake_minimum_required` is called first 
            "# Copyright 2021 Google LLC": "# Copyright 2021 Google LLC\ncmake_minimum_required(VERSION 3.13)", 
        }

        for pattern, patch in patches.items():
            replace_in_file(self, cmakelists, pattern, patch)

        # 1. Allow Shared builds
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "ruy_cc_library.cmake"),
                              "add_library(${_NAME} STATIC",
                              "add_library(${_NAME}"
                              )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["ruy_frontend",
                            "ruy_context",
                            "ruy_trmul",
                            "ruy_thread_pool",
                            "ruy_blocking_counter",
                            "ruy_prepare_packed_matrices",
                            "ruy_ctx",
                            "ruy_allocator",
                            "ruy_prepacked_cache",
                            "ruy_tune",
                            "ruy_wait",
                            "ruy_apply_multiplier",
                            "ruy_block_map",
                            "ruy_context_get_ctx",
                            "ruy_cpuinfo",
                            "ruy_denormal",
                            "ruy_have_built_path_for_avx",
                            "ruy_have_built_path_for_avx2_fma",
                            "ruy_have_built_path_for_avx512",
                            "ruy_kernel_arm",
                            "ruy_kernel_avx",
                            "ruy_kernel_avx2_fma",
                            "ruy_kernel_avx512",
                            "ruy_pack_arm",
                            "ruy_pack_avx",
                            "ruy_pack_avx2_fma",
                            "ruy_pack_avx512",
                            "ruy_system_aligned_alloc",
                            "ruy_profiler_instrumentation",
                            "ruy_profiler_profiler"
                            ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
