import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class OnnxRuntimeConan(ConanFile):
    name = "onnxruntime"
    description = "ONNX Runtime: cross-platform, high performance scoring " \
                  "engine for ML models https://aka.ms/onnxruntime"
    license = "MIT License"
    topics = (
        "deep-learning",
        "onnx",
        "neural-networks",
        "machine-learning",
        "ai-framework",
        "hardware-acceleration"
    )
    homepage = "https://www.onnxruntime.ai/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "force_min_size_rel": [True, False],
        "with_static_rt": [True, False],
        "with_tvm": [True, False],
        "with_tvm_llvm": [True, False],

        "with_openvino": [True, False],
        "with_cuda": [True, False],
        "with_coreml": [True, False],
        "with_dml": [True, False],
        "with_openmp": [True, False],
        "with_dnnl": [True, False],
        "with_nnapi": [True, False],
        "with_winml": [True, False],

        "with_python": [True, False],
        "with_csharp": [True, False],
        "with_java": [True, False],
        "with_tests": [True, False],
        "with_benchmarks": [True, False],

        "with_bitcode": [True, False],
    }

    generators = "cmake", "cmake_find_package"

    default_options = {k: False for k, _ in options.items()}

    exports_sources = ['patches/*']

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        if tools.cross_building(self) and hasattr(self, "settings_build"):
            self.build_requires("protobuf/3.17.1")

    def requirements(self):
        self.requires("protobuf/3.17.1")
        self.requires("date/3.0.0")
        self.requires("re2/20210401")
        self.requires("onnx/1.9.0")
        self.requires("flatbuffers/1.12.0")
        self.requires("boost/1.76.0")       # for mp11
        self.requires("nsync/1.23.0")
        self.requires("optional-lite/3.4.0")
        self.requires("safeint/3.0.26")
        self.requires("nlohmann_json/3.9.1")
        self.requires("eigen/3.4.0")

    def configure(self):
        if self.settings.os == "Android" or self.settings.os == "iOS":
            self.options["flatbuffers"].flatc = False

        self.options["boost"].header_only = True
        self.options["boost"].without_chrono = False
        self.options["boost"].without_context = False
        self.options["boost"].without_system = False
        self.options["boost"].without_timer = False

    def validate(self):
        if self.options.with_dnnl:
            raise ConanInvalidConfiguration(
                "Option 'with_dnnl' not supported yet! "
                "Add receipt for https://github.com/oneapi-src/onednn")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True,
                  destination=self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @property
    def _cmake_rt_def(self):
        if self.settings.compiler == "Visual Studio":
            return "MSVC_STATIC_RUNTIME"
        return "GCC_STATIC_CPP_RUNTIME"

    def _add_definition(self, definition, value):
        if isinstance(value, bool):
            value = "ON" if value else "OFF"

        self._cmake.definitions[f"onnxruntime_{definition}"] = value

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._add_definition("PREFER_SYSTEM_LIB", True)

        with_tests = self.options.with_tests
        if not tools.cross_building(self):
            self._add_definition("RUN_ONNX_TESTS", with_tests)
            self._add_definition("RUN_MODELTEST_IN_DEBUG_MODE", with_tests)
            self._add_definition("FUZZ_TEST", with_tests)

        self._add_definition("USE_VALGRIND", False)

        self._add_definition("BUILD_SHARED_LIB", self.options.shared)
        self._add_definition("BUILD_UNIT_TESTS", self.options.with_tests)
        self._add_definition("BUILD_BENCHMARKS", self.options.with_benchmarks)
        self._add_definition("BUILD_FOR_NATIVE_MACHINE", False)  # ??
        self._add_definition("BUILD_WEBASSEMBLY", False)

        self._add_definition("GENERATE_TEST_REPORTS", self.options.with_tests)

        self._add_definition("ENABLE_STATIC_ANALYSIS", False)
        self._add_definition("ENABLE_MEMLEAK_CHECKER", False)
        self._add_definition("ENABLE_CUDA_LINE_NUMBER_INFO", False)  # True may cause LNK1169 error
        self._add_definition("ENABLE_LTO", False)
        self._add_definition("ENABLE_INSTRUMENT", False)
        self._add_definition("ENABLE_WEBASSEMBLY_EXCEPTION_CATCHING", False)

        self._add_definition("ENABLE_PYTHON", self.options.with_python)
        self._add_definition("BUILD_CSHARP", self.options.with_csharp)
        self._add_definition("USE_CUDA", self.options.with_cuda)

        self._add_definition("USE_OPENVINO", self.options.with_openvino)

        if self.settings.os == "iOS" or self.settings.os == "Macos":
            self._add_definition("USE_COREML", self.options.with_coreml)
        if self.settings.os == "Android":
            self._add_definition("USE_NNAPI_BUILTIN", self.options.with_nnapi)

        self._add_definition("USE_RKNPU", False)
        self._add_definition("USE_DNNL", self.options.with_dnnl)
        self._add_definition("USE_FEATURIZERS", False)
        self._add_definition("DEV_MODE", False)
        self._add_definition(self._cmake_rt_def, self.options.with_static_rt)

        self._add_definition("USE_PREINSTALLED_EIGEN", True)
        eigen_includedir = self.deps_cpp_info["eigen"].include_paths[0]
        self._cmake.definitions["eigen_SOURCE_PATH"] = eigen_includedir

        self._add_definition("USE_TVM", self.options.with_tvm)
        self._add_definition("USE_LLVM", self.options.with_tvm_llvm)

        self._add_definition("USE_AVX", False)
        self._add_definition("USE_AVX2", False)
        self._add_definition("USE_AVX512", False)

        self._add_definition("USE_OPENMP", False)
        self._add_definition("ENABLE_MICROSOFT_INTERNAL", False)
        self._add_definition("USE_NUPHAR", False)
        self._add_definition("USE_VITISAI", False)
        self._add_definition("USE_TENSORRT", False)
        self._add_definition("CROSS_COMPILING", False)
        self._add_definition("GCOV_COVERAGE", False)

        # It's preferred to turn it OFF when onnxruntime
        # is dynamically linked to PROTOBUF
        self._add_definition("USE_FULL_PROTOBUF", False)
        self._cmake.definitions["tensorflow_C_PACKAGE_PATH"] = None
        self._add_definition("ENABLE_LANGUAGE_INTEROP_OPS", False)
        self._add_definition("DEBUG_NODE_INPUTS_OUTPUTS", False)
        self._add_definition("USE_DML", False)
        self._add_definition("USE_MIGRAPHX", False)
        self._add_definition("USE_WINML", self.options.with_winml)
        self._add_definition("USE_ACL", False)
        self._add_definition("USE_ACL_1902", False)
        self._add_definition("USE_ACL_1905", False)
        self._add_definition("USE_ACL_1908", False)
        self._add_definition("USE_ACL_2002", False)
        self._add_definition("USE_ARMNN", False)
        self._add_definition("ARMNN_RELU_USE_CPU", True)
        self._add_definition("ARMNN_BN_USE_CPU", True)
        self._add_definition("USE_TELEMETRY", False)

        self._add_definition("USE_ROCM", False)

        # Options related to reducing the binary size produced by the build
        self._add_definition("DISABLE_CONTRIB_OPS", False)
        self._add_definition("DISABLE_ML_OPS", False)
        self._add_definition("DISABLE_RTTI", False)

        # For now onnxruntime_DISABLE_EXCEPTIONS will only work with
        #   onnxruntime_MINIMAL_BUILD, more changes (ONNX, non-CPU EP, ...)
        #   are required to run this standalone
        self._add_definition("DISABLE_EXCEPTIONS", False)
        self._add_definition("MINIMAL_BUILD", False)
        self._add_definition("EXTENDED_MINIMAL_BUILD", False)
        self._add_definition("MINIMAL_BUILD_CUSTOM_OPS", False)
        self._add_definition("REDUCED_OPS_BUILD", False)
        self._add_definition("DISABLE_ORT_FORMAT_LOAD", False)

        # training options
        self._add_definition("ENABLE_NVTX_PROFILE", False)
        self._add_definition("ENABLE_MEMORY_PROFILE", False)
        self._add_definition("ENABLE_TRAINING", False)
        self._add_definition("ENABLE_TRAINING_OPS", False)
        self._add_definition("ENABLE_TRAINING_E2E_TESTS", False)
        self._add_definition("ENABLE_CPU_FP16_OPS", False)
        self._add_definition("USE_NCCL", False)
        self._add_definition("USE_MPI", False)

        # Enable bitcode for iOS
        if self.settings.os == "iOS" or self.settings.os == "Macos":
            self._add_definition("ENABLE_BITCODE", self.options.with_bitcode)

        self._cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder

        if self.options.force_min_size_rel:
            self._cmake.definitions["CMAKE_BUILD_TYPE"] = "MinSizeRel"
        elif self.settings.build_type is not None:
            build_type = str(self.settings.build_type)
            self._cmake.definitions["CMAKE_BUILD_TYPE"] = build_type

        if self.settings.os == "Android":
            android_ndk_root = None
            android_sdk_root = None
            if "ANDROID_NDK_ROOT" in os.environ:
                android_ndk_root = os.environ.get("ANDROID_NDK_ROOT")
            elif "ANDROID_NDK_HOME" in os.environ:
                android_ndk_root = os.environ.get("ANDROID_NDK_HOME")

            if "ANDROID_SDK_ROOT" in os.environ:
                android_sdk_root = os.environ.get("ANDROID_SDK_ROOT")
            elif "ANDROID_SDK_HOME" in os.environ:
                android_sdk_root = os.environ.get("ANDROID_SDK_HOME")
            elif "ANDROID_HOME" in os.environ:
                android_sdk_root = os.environ.get("ANDROID_HOME")

            if android_ndk_root is None:
                ndk_bundle_path = os.path.join(android_sdk_root, "ndk-bundle")
                if os.path.isdir(ndk_bundle_path):
                    android_ndk_root = ndk_bundle_path

            if android_ndk_root is None:
                raise Exception("ANDROID_NDK_ROOT env not defined")
            if android_sdk_root is None:
                raise Exception("ANDROID_SDK_ROOT env not defined")

            self._cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
                android_ndk_root, 'build', 'cmake', 'android.toolchain.cmake')
            api_level = str(self.settings.os.api_level)
            android_abi = tools.to_android_abi(self.settings.arch)
            self._cmake.definitions["ANDROID_PLATFORM"] = \
                f"android-{api_level}"
            self._cmake.definitions["ANDROID_ABI"] = android_abi
            self._cmake.definitions["ANDROID_MIN_SDK"] = api_level

        self._cmake.definitions["ONNX_CUSTOM_PROTOC_EXECUTABLE"] = \
            tools.which('protoc')

        src_folder = os.path.join(self._source_subfolder, 'cmake')
        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=src_folder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        if self.options.shared:
            self.copy(pattern="*.so", dst="lib", src=self._build_subfolder)
            self.copy(pattern="*.dll", dst="lib", src=self._build_subfolder)
        else:
            self.copy(pattern="*.a", dst="lib", src=self._build_subfolder)

        if self.options.with_tests:
            self.copy(
                "onnxruntime_perf_test",
                dst="bin",
                keep_path=False
            )

        providers_inc = "include/onnxruntime/core/providers"
        for provider in ["nnapi", "dnnl"]:
            if getattr(self.options, f"with_{provider}"):
                dst = os.path.join(providers_inc, provider)
                self.copy(
                    pattern="*.h",
                    dst=dst,
                    src=os.path.join(self.name, dst)
                )

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "OnnxRuntime"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OnnxRuntime"
        self.cpp_info.names["cmake_find_package"] = "OnnxRuntime"
        self.cpp_info.names["cmake_find_package_multi"] = "OnnxRuntime"

        if self.options.shared:
            self.cpp_info.libs = ["onnxruntime"]
        else:
            debug_suffix = "d" if self.settings.build_type == "Debug" else ""

            onnxruntime_libs = []

            if self.options.with_nnapi:
                onnxruntime_libs.append("providers_nnapi")

            onnxruntime_libs.extend([
                "session",
                "optimizer",
                "providers",
                "framework",
                "graph",
                "util",
                "mlas",
                "common",
                "flatbuffers",
            ])

            self.cpp_info.libs = \
                [f"onnxruntime_{lib}" for lib in onnxruntime_libs]

        self.cpp_info.includedirs.append("include/onnxruntime/core/session")
