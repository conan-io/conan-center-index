import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class CutlassConan(ConanFile):
    name = "cutlass"
    description = "CUTLASS: CUDA Templates for Linear Algebra Subroutines"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("linear-algebra", "gpu", "cuda", "deep-learning", "nvidia", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    # TODO: add header_only=False option

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "7",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # Install via CMake to ensure headers are configured correctly
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_SUPPRESS_REGENERATION"] = True
        tc.cache_variables["CUTLASS_REVISION"]=f"v{self.version}"
        tc.cache_variables["CUTLASS_NATIVE_CUDA"] = False
        tc.cache_variables["CUTLASS_ENABLE_HEADERS_ONLY"] = True
        tc.cache_variables["CUTLASS_ENABLE_TOOLS"] = False
        tc.cache_variables["CUTLASS_ENABLE_LIBRARY"] = False
        tc.cache_variables["CUTLASS_ENABLE_PROFILER"] = False
        tc.cache_variables["CUTLASS_ENABLE_PERFORMANCE"] = False
        tc.cache_variables["CUTLASS_ENABLE_TESTS"] = False
        tc.cache_variables["CUTLASS_ENABLE_GTEST_UNIT_TESTS"] = False
        tc.cache_variables["CUTLASS_ENABLE_CUBLAS"] = False
        tc.cache_variables["CUTLASS_ENABLE_CUDNN"] = False
        tc.generate()
        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        # Don't look for CUDA, we're only installing the headers
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "include(${CMAKE_CURRENT_SOURCE_DIR}/CUDA.cmake)",
                                                                                 """
                                                                                 if(NOT CUTLASS_ENABLE_HEADERS_ONLY)
                                                                                 include(${CMAKE_CURRENT_SOURCE_DIR}/CUDA.cmake)
                                                                                 endif()""")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "test"))


    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NvidiaCutlass")
        self.cpp_info.set_property("cmake_target_name", "nvidia::cutlass::cutlass")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
