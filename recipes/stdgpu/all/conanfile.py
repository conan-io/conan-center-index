import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
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
        "openmp": ["llvm", "system"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "openmp",
        "setup_compiler_flags": False,
        "enable_contract_checks": None,
        "use_32_bit_index": True,
        "openmp": "llvm",
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
                "msvc": "192",
                "Visual Studio": "16",
            }
        else:
            # > 1.3.0
            # Based on https://github.com/stotko/stdgpu/tree/32e0517#building
            return {
                "gcc": "9",
                "clang": "10",
                "apple-clang": "12",
                "msvc": "192",
                "Visual Studio": "16",
            }

    def export_sources(self):
        copy(self, "cmake/*", dst=self.export_sources_folder, src=self.recipe_folder)

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

    def package_id(self):
        if self.info.options.backend != "openmp":
            del self.info.options.openmp

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backend != "hip":
            self.requires("thrust/1.17.2", transitive_headers=True)
        else:
            # The baseline Thrust version provided by Nvidia and Conan is not compatible with HIP.
            self.output.warning("HIP support requires Thrust with ROCm. "
                                "Using Thrust from system instead of Conan.")
        if self.options.backend == "openmp":
            if self.options.openmp == "llvm":
                self.requires("llvm-openmp/12.0.1", transitive_headers=True, transitive_libs=True)
            else:
                self.output.info("Using OpenMP backend with system OpenMP")

    def build_requirements(self):
        if Version(self.version) > "1.3.0":
            self.tool_requires("cmake/[>=3.18 <4]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_min_versions.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.options.backend == "cuda" and self.dependencies["thrust"].options.device_system != "cuda":
            raise ConanInvalidConfiguration(f"{self.ref} option backend=cuda should use '-o thrust/*:device_system=cuda' as well.")
        if self.options.backend == "openmp" and self.dependencies["thrust"].options.device_system != "omp":
            raise ConanInvalidConfiguration(f"{self.ref} option backend=openmp should use '-o thrust/*:device_system=omp' as well.")

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
        tc.variables["STDGPU_BUILD_TESTS"] = False
        tc.variables["STDGPU_BUILD_TEST_COVERAGE"] = False
        tc.variables["STDGPU_ANALYZE_WITH_CLANG_TIDY"] = False
        tc.variables["STDGPU_ANALYZE_WITH_CPPCHECK"] = False
        if self.options.enable_contract_checks is not None:
            tc.variables["STDGPU_ENABLE_CONTRACT_CHECKS"] = self.options.enable_contract_checks
        tc.variables["STDGPU_USE_32_BIT_INDEX"] = self.options.use_32_bit_index
        tc.preprocessor_definitions["THRUST_IGNORE_CUB_VERSION_CHECK"] = "1"
        tc.generate()
        deps = CMakeDeps(self)
        # FIXME: should be set by the thrust recipe instead
        deps.set_property("thrust", "cmake_find_mode", "both")
        deps.set_property("openmp", "cmake_find_mode", "both")
        deps.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def _patch_sources(self):
        # Fix repeated application of the THRUST_DEVICE_SYSTEM define
        for backend in ["cuda", "openmp"]:
            replace_in_file(self, os.path.join(self.source_folder, "src", "stdgpu", backend, "CMakeLists.txt"),
                            "THRUST_DEVICE_SYSTEM=",
                            ") # THRUST_DEVICE_SYSTEM=")
        replace_in_file(self, os.path.join(self.source_folder, "src", "stdgpu", "openmp", "CMakeLists.txt"),
                        "find_package(OpenMP 2.0 REQUIRED)",
                        "find_package(OpenMP REQUIRED)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        copy(self, "*.cmake",
             dst=os.path.join(self.package_folder, "lib", "cmake"),
             src=os.path.join(self.export_sources_folder, "cmake"))

    def _configure_system_openmp(self):
        openmp_flags = []
        if is_msvc(self):
            openmp_flags = ["-openmp"]
        elif self.settings.compiler in ["clang", "apple-clang"]:
            openmp_flags = ["-Xpreprocessor", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            openmp_flags = ["-fopenmp"]
        elif self.settings.compiler == "intel":
            openmp_flags = ["/Qopenmp"] if self.settings.os == "Windows" else ["-Qopenmp"]
        self.cpp_info.cflags += openmp_flags
        self.cpp_info.cxxflags += openmp_flags
        self.cpp_info.sharedlinkflags += openmp_flags
        self.cpp_info.exelinkflags += openmp_flags
        if self.settings.os == "Windows":
            if is_msvc(self):
                self.cpp_info.system_libs.append("delayimp")
            elif self.settings.compiler == "gcc":
                self.cpp_info.system_libs.append("gomp")

    def package_info(self):
        self.cpp_info.libs = ["stdgpu"]

        if self.options.backend == "openmp":
            if self.options.openmp == "system":
                self._configure_system_openmp()
        elif self.options.backend == "cuda":
            module_path = os.path.join("lib", "cmake", "stdgpu-dependencies-cuda.cmake")
            self.cpp_info.set_property("cmake_build_modules", [module_path])
        elif self.options.backend == "hip":
            module_path = os.path.join("lib", "cmake", "stdgpu-dependencies-hip.cmake")
            self.cpp_info.set_property("cmake_build_modules", [module_path])
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
