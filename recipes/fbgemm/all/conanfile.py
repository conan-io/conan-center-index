import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, export_conandata_patches, get, apply_conandata_patches, replace_in_file, save, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class FbgemmConan(ConanFile):
    name = "fbgemm"
    description = ("FBGEMM (Facebook GEneral Matrix Multiplication) is a "
                   "low-precision, high-performance matrix-matrix multiplications "
                   "and convolution library for server-side inference.")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pytorch/FBGEMM"
    topics = ("matrix", "convolution", "linear-algebra", "machine-learning")

    package_type = "library"
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
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "6",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("asmjit/cci.20210306")
        self.requires("cpuinfo/cci.20231129")
        # self.requires("openmp/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_fbgemm_INCLUDE"] = "conan_deps.cmake"
        tc.variables["FBGEMM_LIBRARY_TYPE"] = "shared" if self.options.shared else "static"
        tc.variables["FBGEMM_BUILD_TESTS"] = False
        tc.variables["FBGEMM_BUILD_BENCHMARKS"] = False
        tc.variables["FBGEMM_BUILD_DOCS"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("asmjit", "cmake_target_name", "asmjit")
        deps.set_property("cpuinfo", "cmake_target_name", "cpuinfo")
        deps.generate()

        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Don't inject definitions from upstream dependencies
        replace_in_file(self, cmakelists, "target_compile_definitions(fbgemm_generic PRIVATE ASMJIT_STATIC)", "")
        replace_in_file(self, cmakelists, "target_compile_definitions(fbgemm_avx2 PRIVATE ASMJIT_STATIC)", "")
        replace_in_file(self, cmakelists, "target_compile_definitions(fbgemm_avx512 PRIVATE ASMJIT_STATIC)", "")
        # Honor runtime from profile
        replace_in_file(self, cmakelists, 'if(${flag_var} MATCHES "/MD")', "if(0)")
        # Do not install stuff related to dependencies
        replace_in_file(self, cmakelists, 'if(MSVC)\n  if(FBGEMM_LIBRARY_TYPE STREQUAL "shared")', "if(0)\nif(0)")
        # Properly link to obj targets
        replace_in_file(self, cmakelists,
                              "add_dependencies(fbgemm asmjit cpuinfo)",
                              "target_link_libraries(fbgemm_generic asmjit cpuinfo)\n"
                              "target_link_libraries(fbgemm_avx2 asmjit cpuinfo)\n"
                              "target_link_libraries(fbgemm_avx512 asmjit cpuinfo)")
        # Disable third-party subdirs
        save(self, os.path.join(self.source_folder, "third_party", "asmjit", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "third_party", "cpuinfo", "CMakeLists.txt"), "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fbgemmLibrary")
        self.cpp_info.set_property("cmake_target_name", "fbgemm")
        self.cpp_info.libs = ["fbgemm"]
        if not self.options.shared:
            self.cpp_info.defines = ["FBGEMM_STATIC"]
