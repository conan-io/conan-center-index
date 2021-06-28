import os
from conans import ConanFile, CMake, tools


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

    settings = "os", "compiler", "build_type", "arch", "os_build"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
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

    default_options = {k: k == "fPIC" for k, _ in options.items()}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        self.requires("protobuf/3.15.5")

    def requirements(self):
        self.requires("protobuf/3.15.5")
        self.requires("date/3.0.0")
        self.requires("re2/20210401")
        self.requires("onnx/1.8.1")
        self.requires("flatbuffers/1.12.0")
        self.requires("boost/1.76.0")       # for mp11

    def configure(self):
        if self.settings.os == "Android" or self.settings.os == "iOS":
            self.options["flatbuffers"].flatc = False

        self.options["boost"].header_only = True
        self.options["boost"].without_chrono = False
        self.options["boost"].without_context = False
        self.options["boost"].without_system = False
        self.options["boost"].without_timer = False

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(f"onnxruntime-{self.version}", self._source_subfolder)

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

        #The onnxruntime_PREFER_SYSTEM_LIB is mainly designed for package managers like apt/yum/vcpkg.
        #Please note, by default Protobuf_USE_STATIC_LIBS is OFF but it's recommended to turn it ON on Windows. You should set it properly when onnxruntime_PREFER_SYSTEM_LIB is ON otherwise you'll hit linkage errors.
        #If you have already installed protobuf(or the others) in your system at the default system paths(like /usr/include), then it's better to set onnxruntime_PREFER_SYSTEM_LIB ON. Otherwise onnxruntime may see two different protobuf versions and we won't know which one will be used, the worst case could be onnxruntime picked up header files from one of them but the binaries from the other one.
        #It's default OFF because it's experimental now.
        self._add_definition("PREFER_SYSTEM_LIB", True)
        self._cmake.definitions["re2_FOUND"] = "ON"
        self._cmake.definitions["re2_INCLUDE_DIRS"] = self.deps_cpp_info["re2"].include_paths
        self._cmake.definitions["re2_LIBRARIES"] = self.deps_cpp_info["re2"].lib_paths

        # Options
        self._add_definition("RUN_ONNX_TESTS", self.options.with_tests)
        self._add_definition("GENERATE_TEST_REPORTS", self.options.with_tests)
        self._add_definition("ENABLE_STATIC_ANALYSIS", False)
        self._add_definition("ENABLE_PYTHON", self.options.with_python)

        # Enable it may cause LNK1169 error
        self._add_definition("ENABLE_MEMLEAK_CHECKER", False)
        self._add_definition("USE_CUDA", self.options.with_cuda)
        self._add_definition("ENABLE_CUDA_LINE_NUMBER_INFO", False)
        self._add_definition("USE_OPENVINO", self.options.with_openvino)
        if self.settings.os == "iOS" or self.settings.os == "Macos":
            self._add_definition("USE_COREML", self.options.with_coreml)
        if self.settings.os == "Android":
            self._add_definition("USE_NNAPI_BUILTIN", self.options.with_nnapi)
        # self._add_definition("USE_RKNPU", self.options.with_rknpu)
        self._add_definition("USE_DNNL", self.options.with_dnnl)
        # self._add_definition("USE_FEATURIZERS", self.options.with_featurizers)
        self._add_definition("DEV_MODE", False)
        self._add_definition(self._cmake_rt_def, self.options.with_static_rt)
        self._add_definition("BUILD_UNIT_TESTS", self.options.with_tests)
        self._add_definition("BUILD_CSHARP", self.options.with_csharp)
        self._add_definition("USE_PREINSTALLED_EIGEN", False)
        self._add_definition("BUILD_BENCHMARKS", self.options.with_benchmarks)

        self._add_definition("USE_TVM", self.options.with_tvm)
        self._add_definition("USE_LLVM", self.options.with_tvm_llvm)

        self._add_definition("BUILD_FOR_NATIVE_MACHINE", False)
        self._add_definition("USE_AVX", False)
        self._add_definition("USE_AVX2", False)
        self._add_definition("USE_AVX512", False)

        self._add_definition("USE_OPENMP", False)
        self._add_definition("BUILD_SHARED_LIB", self.options.shared)
        self._add_definition("ENABLE_MICROSOFT_INTERNAL", False)
        self._add_definition("USE_NUPHAR", False)
        self._add_definition("USE_VITISAI", False)
        self._add_definition("USE_TENSORRT", False)
        self._add_definition("ENABLE_LTO", False)
        self._add_definition("CROSS_COMPILING", False)
        self._add_definition("GCOV_COVERAGE", False)

        #It's preferred to turn it OFF when onnxruntime is dynamically linked to PROTOBUF
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
        self._add_definition("ENABLE_INSTRUMENT", False)
        self._add_definition("USE_TELEMETRY", False)

        self._add_definition("USE_ROCM", False)

        # Options related to reducing the binary size produced by the build
        self._add_definition("DISABLE_CONTRIB_OPS", False)
        self._add_definition("DISABLE_ML_OPS", False)
        self._add_definition("DISABLE_RTTI", False)
        # For now onnxruntime_DISABLE_EXCEPTIONS will only work with onnxruntime_MINIMAL_BUILD, more changes (ONNX, non-CPU EP, ...) are required to run this standalone
        self._add_definition("DISABLE_EXCEPTIONS", False)
        self._add_definition("MINIMAL_BUILD", False)
        self._add_definition("EXTENDED_MINIMAL_BUILD", False)
        self._add_definition("MINIMAL_BUILD_CUSTOM_OPS", False)
        self._add_definition("REDUCED_OPS_BUILD", False)
        self._add_definition("DISABLE_ORT_FORMAT_LOAD", False)

        #A special option just for debugging and sanitize check. Please do not enable in option in retail builds.
        #The option has no effect on Windows.
        self._add_definition("USE_VALGRIND", False)

        # A special build option only used for gathering code coverage info
        self._add_definition("RUN_MODELTEST_IN_DEBUG_MODE", False)

        # options for security fuzzing
        # build configuration for fuzz testing is in onnxruntime_fuzz_test.cmake
        self._add_definition("FUZZ_TEST", False)

        # training options
        self._add_definition("ENABLE_NVTX_PROFILE", False)
        self._add_definition("ENABLE_MEMORY_PROFILE", False)
        self._add_definition("ENABLE_TRAINING", False)
        self._add_definition("ENABLE_TRAINING_OPS", False)
        self._add_definition("ENABLE_TRAINING_E2E_TESTS", False)
        self._add_definition("ENABLE_CPU_FP16_OPS", False)
        self._add_definition("USE_NCCL", False)
        self._add_definition("USE_MPI", False)

        # build WebAssembly
        self._add_definition("BUILD_WEBASSEMBLY", False)
        self._add_definition("ENABLE_WEBASSEMBLY_EXCEPTION_CATCHING", False)

        # Enable bitcode for iOS
        if self.settings.os == "iOS" or self.settings.os == "Macos":
            self._add_definition("ENABLE_BITCODE", self.options.with_bitcode)

        self._cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder

        if self.options.force_min_size_rel:
            self._cmake.definitions["CMAKE_BUILD_TYPE"] = "MinSizeRel"
        elif self.settings.build_type is not None:
            self._cmake.definitions["CMAKE_BUILD_TYPE"] = str(self.settings.build_type)

        # TODO full list of options in
        # https://github.com/microsoft/onnxruntime/blob/master/BUILD.md

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

            # TODO ENV["ANDROID_SDK_ROOT"]

            self._cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.path.join(
                android_ndk_path, 'build', 'cmake', 'android.toolchain.cmake')
            self._cmake.definitions["ANDROID_PLATFORM"] = "android-" + str(self.settings.os.api_level)
            self._cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(self.settings.arch)
            self._cmake.definitions["ANDROID_MIN_SDK"] = str(self.settings.os.api_level)

        self._cmake.definitions["ONNX_CUSTOM_PROTOC_EXECUTABLE"] = tools.which('protoc')

        self._cmake.configure(source_folder=os.path.join(self._source_subfolder, 'cmake'), build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        build_dir = self._onnxruntime_build_dir

        cmake = self._configure_cmake()
        cmake.install()

        if not self.options.shared:
            self.copy(pattern="*.a", dst="lib", src=build_dir, keep_path=False)

        self.copy(
            "onnxruntime_perf_test",
            dst="bin",
            src=build_dir,
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

            self.cpp_info.libs.extend([
                "onnx",
                "onnx_proto",
                "flatbuffers",
                "re2",
                "nsync_cpp",
                "protobuf-lite" + debug_suffix,
            ])

            if self.options.with_dnnl:
                self.cpp_info.libs.append("dnnl")

        self.cpp_info.includedirs.append("include/onnxruntime/core/session")

    @property
    def _onnxruntime_build_dir(self):
        msr = self.options.force_min_size_rel
        build_type = "MinSizeRel" if msr else str(self.settings.build_type)
        return os.path.join(
            self.build_folder,
            self._source_subfolder,
            "build",
            str(self.settings.os),
            build_type
        )
