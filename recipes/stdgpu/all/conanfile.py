import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class StdgpuConan(ConanFile):
    name = "stdgpu"
    description = "Efficient STL-like Data Structures on the GPU"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://stotko.github.io/stdgpu/"
    topics = ("cuda", "data-structures", "gpgpu", "gpu", "hip", "openmp", "rocm", "stl", "thrust")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["cuda", "openmp", "hip"],
        "setup_compiler_flags": [True, False],
        "enable_contract_checks": [None, True, False],
        "use_32_bit_index": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "openmp",
        "setup_compiler_flags": False,
        "enable_contract_checks": None,
        "use_32_bit_index": True,
    }

    @property
    def _min_cppstd(self):
        if self.version == "1.3.0":
            return 14
        else:
            return 17

    @property
    def _compilers_min_versions(self):
        if self.version == "1.3.0":
            # Based on https://github.com/stotko/stdgpu/tree/1.3.0#building
            return {
                "gcc": "7",
                "clang": "6",
                "apple-clang": "6",
                "msvc": "19.20",
                "Visual Studio": "16",
            }
        else:
            # > 1.3.0
            # Based on https://github.com/stotko/stdgpu/tree/32e0517#building
            return {
                "gcc": "9",
                "clang": "10",
                "apple-clang": "12",
                "msvc": "19.20",
                "Visual Studio": "16",
            }

    @property
    def _tests_enabled(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.backend == "cuda":
            self.options["thrust"].device_system = "cuda"
        elif self.options.backend == "openmp":
            self.options["thrust"].device_system = "omp"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backend != "hip":
            # HIP support requires Thrust provided with ROCm.
            # The main version provided by Nvidia found in Conan is not compatible.
            self.requires("thrust/1.17.2", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_min_versions.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # All the main params from https://github.com/stotko/#integration
        backend = str(self.options.backend).upper()
        tc.variables["STDGPU_BACKEND"] = f"STDGPU_BACKEND_{backend}"
        tc.variables["STDGPU_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["STDGPU_SETUP_COMPILER_FLAGS"] = self.options.setup_compiler_flags
        tc.variables["STDGPU_TREAT_WARNINGS_AS_ERRORS"] = False
        tc.variables["STDGPU_BUILD_EXAMPLES"] = False
        tc.variables["STDGPU_BUILD_BENCHMARKS"] = False
        tc.variables["STDGPU_BUILD_TESTS"] = self._tests_enabled
        tc.variables["STDGPU_BUILD_TEST_COVERAGE"] = False
        tc.variables["STDGPU_ANALYZE_WITH_CLANG_TIDY"] = False
        tc.variables["STDGPU_ANALYZE_WITH_CPPCHECK"] = False
        if self.options.enable_contract_checks is not None:
            tc.variables["STDGPU_ENABLE_CONTRACT_CHECKS"] = self.options.enable_contract_checks
        tc.variables["STDGPU_USE_32_BIT_INDEX"] = self.options.use_32_bit_index
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self._tests_enabled:
            cmake.test()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rm(self, "*[.pdb|.la]", self.package_folder)

    def package_info(self):
        self.cpp_info.libs = ["stdgpu"]

        if self.options.backend == "openmp":
            if is_msvc(self) and not self.options.shared:
                self.cpp_info.cxxflags += ["-openmp"]
                self.cpp_info.system_libs += ["VCOMP"]
            elif self.settings.compiler == "gcc":
                self.cpp_info.cxxflags += ["-fopenmp"]
                self.cpp_info.system_libs += ["gomp"]
            elif self.settings.compiler in ("clang", "apple-clang"):
                self.cpp_info.cxxflags += ["-Xpreprocessor", "-fopenmp"]
                self.cpp_info.system_libs += ["omp"]
