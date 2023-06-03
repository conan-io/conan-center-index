from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
import os
import sys


required_conan_version = ">=1.53.0"


class OnnxRuntimeConan(ConanFile):
    name = "onnxruntime"
    description = "ONNX Runtime: cross-platform, high performance ML inferencing and training accelerator"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://onnxruntime.ai"
    topics = ("deep-learning", "onnx", "neural-networks", "machine-learning", "ai-framework", "hardware-acceleration")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_xnnpack": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_xnnpack": False,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "5",
            "apple-clang": "10",
        }

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

    @property
    def _onnx_version(self):
        return {
            "1.14.1": "1.13.1",
            "1.15.0": "1.14.0",
        }[self.version]

    def requirements(self):
        self.requires("abseil/20230125.2")
        self.requires("protobuf/3.21.9")
        self.requires("date/3.0.1")
        self.requires("re2/20230301")
        self.requires(f"onnx/{self._onnx_version}")
        self.requires("flatbuffers/1.12.0")
        self.requires("boost/1.81.0", headers=True, libs=False, run=False)  # for mp11, header only, no need for libraries to link/run
        self.requires("safeint/3.0.28")
        self.requires("nlohmann_json/3.11.2")
        self.requires("eigen/3.4.0")
        self.requires("ms-gsl/4.0.0")
        self.requires("cpuinfo/cci.20220228")
        if self.settings.os != "Windows":
            self.requires("nsync/1.25.0")
        else:
            self.requires("wil/1.0.230202.1")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20220801")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.version >= Version("1.15.0") and self.options.shared and sys.version_info[:2] < (3, 8):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires python 3.8+ to be built as shared."
            )

    def build_requirements(self):
        # Required by upstream https://github.com/microsoft/onnxruntime/blob/v1.14.1/cmake/CMakeLists.txt#L5
        self.tool_requires("cmake/[>=3.24 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # disable downloading dependencies to ensure conan ones are used
        tc.variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True
        if self.version >= Version("1.15.0") and self.options.shared:
            tc.variables["Python_EXECUTABLE"] = sys.executable

        tc.variables["onnxruntime_BUILD_SHARED_LIB"] = self.options.shared
        tc.variables["onnxruntime_USE_FULL_PROTOBUF"] = not self.dependencies["protobuf"].options.lite
        tc.variables["onnxruntime_USE_XNNPACK"] = self.options.with_xnnpack

        tc.variables["onnxruntime_BUILD_UNIT_TESTS"] = False
        tc.variables["onnxruntime_RUN_ONNX_TESTS"] = False
        tc.variables["onnxruntime_GENERATE_TEST_REPORTS"] = False
        tc.variables["onnxruntime_USE_MIMALLOC"] = False
        tc.variables["onnxruntime_ENABLE_PYTHON"] = False
        tc.variables["onnxruntime_BUILD_CSHARP"] = False
        tc.variables["onnxruntime_BUILD_JAVA"] = False
        tc.variables["onnxruntime_BUILD_NODEJS"] = False
        tc.variables["onnxruntime_BUILD_OBJC"] = False
        tc.variables["onnxruntime_BUILD_APPLE_FRAMEWORK"] = False
        tc.variables["onnxruntime_USE_DNNL"] = False
        tc.variables["onnxruntime_USE_NNAPI_BUILTIN"] = False
        tc.variables["onnxruntime_USE_RKNPU"] = False
        tc.variables["onnxruntime_USE_LLVM"] = False
        tc.variables["onnxruntime_ENABLE_MICROSOFT_INTERNAL"] = False
        tc.variables["onnxruntime_USE_VITISAI"] = False
        tc.variables["onnxruntime_USE_TENSORRT"] = False
        tc.variables["onnxruntime_SKIP_AND_PERFORM_FILTERED_TENSORRT_TESTS"] = True
        tc.variables["onnxruntime_USE_TENSORRT_BUILTIN_PARSER"] = False
        tc.variables["onnxruntime_TENSORRT_PLACEHOLDER_BUILDER"] = False
        tc.variables["onnxruntime_USE_TVM"] = False
        tc.variables["onnxruntime_TVM_CUDA_RUNTIME"] = False
        tc.variables["onnxruntime_TVM_USE_HASH"] = False
        tc.variables["onnxruntime_CROSS_COMPILING"] = False
        tc.variables["onnxruntime_DISABLE_CONTRIB_OPS"] = False
        tc.variables["onnxruntime_DISABLE_ML_OPS"] = False
        tc.variables["onnxruntime_DISABLE_RTTI"] = False
        tc.variables["onnxruntime_DISABLE_EXCEPTIONS"] = False
        tc.variables["onnxruntime_MINIMAL_BUILD"] = False
        tc.variables["onnxruntime_EXTENDED_MINIMAL_BUILD"] = False
        tc.variables["onnxruntime_MINIMAL_BUILD_CUSTOM_OPS"] = False
        tc.variables["onnxruntime_REDUCED_OPS_BUILD"] = False
        tc.variables["onnxruntime_ENABLE_LANGUAGE_INTEROP_OPS"] = False
        tc.variables["onnxruntime_USE_DML"] = False
        tc.variables["onnxruntime_USE_WINML"] = False
        tc.variables["onnxruntime_BUILD_MS_EXPERIMENTAL_OPS"] = False
        tc.variables["onnxruntime_USE_TELEMETRY"] = False
        tc.variables["onnxruntime_ENABLE_LTO"] = False
        tc.variables["onnxruntime_USE_ACL"] = False
        tc.variables["onnxruntime_USE_ACL_1902"] = False
        tc.variables["onnxruntime_USE_ACL_1905"] = False
        tc.variables["onnxruntime_USE_ACL_1908"] = False
        tc.variables["onnxruntime_USE_ACL_2002"] = False
        tc.variables["onnxruntime_USE_ARMNN"] = False
        tc.variables["onnxruntime_ARMNN_RELU_USE_CPU"] = False
        tc.variables["onnxruntime_ARMNN_BN_USE_CPU"] = False
        tc.variables["onnxruntime_ENABLE_NVTX_PROFILE"] = False
        tc.variables["onnxruntime_ENABLE_TRAINING"] = False
        tc.variables["onnxruntime_ENABLE_TRAINING_OPS"] = False
        tc.variables["onnxruntime_ENABLE_TRAINING_APIS"] = False
        tc.variables["onnxruntime_ENABLE_CPU_FP16_OPS"] = False
        tc.variables["onnxruntime_USE_NCCL"] = False
        tc.variables["onnxruntime_BUILD_BENCHMARKS"] = False
        tc.variables["onnxruntime_USE_ROCM"] = False
        tc.variables["onnxruntime_GCOV_COVERAGE"] = False
        tc.variables["onnxruntime_USE_MPI"] = False
        tc.variables["onnxruntime_ENABLE_MEMORY_PROFILE"] = False
        tc.variables["onnxruntime_ENABLE_CUDA_LINE_NUMBER_INFO"] = False
        tc.variables["onnxruntime_BUILD_WEBASSEMBLY"] = False
        tc.variables["onnxruntime_BUILD_WEBASSEMBLY_STATIC_LIB"] = False
        tc.variables["onnxruntime_ENABLE_WEBASSEMBLY_EXCEPTION_CATCHING"] = False
        tc.variables["onnxruntime_ENABLE_WEBASSEMBLY_API_EXCEPTION_CATCHING"] = False
        tc.variables["onnxruntime_ENABLE_WEBASSEMBLY_EXCEPTION_THROWING"] = False
        tc.variables["onnxruntime_ENABLE_WEBASSEMBLY_THREADS"] = False
        tc.variables["onnxruntime_ENABLE_WEBASSEMBLY_DEBUG_INFO"] = False
        tc.variables["onnxruntime_ENABLE_WEBASSEMBLY_PROFILING"] = False
        tc.variables["onnxruntime_ENABLE_EAGER_MODE"] = False
        tc.variables["onnxruntime_ENABLE_LAZY_TENSOR"] = False
        tc.variables["onnxruntime_ENABLE_EXTERNAL_CUSTOM_OP_SCHEMAS"] = False
        tc.variables["onnxruntime_ENABLE_CUDA_PROFILING"] = False
        tc.variables["onnxruntime_ENABLE_ROCM_PROFILING"] = False
        tc.variables["onnxruntime_USE_CANN"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        vbe = VirtualBuildEnv(self)
        vbe.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        # https://github.com/microsoft/onnxruntime/blob/v1.14.1/cmake/CMakeLists.txt#L792
        # onnxruntime is builds its targets with COMPILE_WARNING_AS_ERROR ON
        # This will most likely lead to build errors on compilers not undergoing CI testing upstream
        # so disable COMPILE_WARNING_AS_ERROR
        cmake.configure(build_script_folder="cmake", cli_args=["--compile-no-warning-as-error"])
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        pkg_config_dir = os.path.join(self.package_folder, "lib", "pkgconfig")
        rmdir(self, pkg_config_dir)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["onnxruntime"]
        else:
            onnxruntime_libs = [
                "session",
                "optimizer",
                "providers",
                "framework",
                "graph",
                "util",
                "mlas",
                "common",
                "flatbuffers",
            ]
            self.cpp_info.libs = [f"onnxruntime_{lib}" for lib in onnxruntime_libs]

        self.cpp_info.includedirs.append("include/onnxruntime/core/session")

        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
        if is_apple_os(self):
            self.cpp_info.frameworks.append("Foundation")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("shlwapi")

        # https://github.com/microsoft/onnxruntime/blob/v1.14.1/cmake/CMakeLists.txt#L1584
        self.cpp_info.set_property("pkg_config_name", "onnxruntime")
