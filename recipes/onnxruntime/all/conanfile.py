import os
from conans import ConanFile, tools


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
        "parallel": [True, False],
        "force_min_size_rel": [True, False],
        "with_dml": [True, False],
        "with_openmp": [True, False],
        "with_dnnl": [True, False],
        "with_nnapi": [True, False],
        "with_winml": [True, False],
        "with_python_wheel": [True, False],
        "with_csharp": [True, False],
        "with_java": [True, False],
        "with_tests": [True, False]
    }

    default_options = {k: False for k, v in options.items()}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("protobuf/3.11.3")

    def source(self):
        # Unfortunatelly git do not pack submodules, so code below doesn't work
        #
        # tools.get(**self.conan_data["sources"][self.version])
        # os.rename(f"onnxruntime-{self.version}", self._source_subfolder)
        #
        # Using tools.Git to get it:
        git = tools.Git(folder=self._source_subfolder)
        git.clone("https://github.com/microsoft/onnxruntime.git")
        git.checkout(f"v{self.version}", submodule="recursive")

    def build(self):
        is_windows = self.settings.os_build == "Windows"
        build_script = ".\\build.bat" if is_windows else "./build.sh"
        build_args = ["--skip_submodule_sync"]

        if self.options.force_min_size_rel:
            build_args.extend(["--config", "MinSizeRel"])
        elif self.settings.build_type is not None:
            build_args.extend(["--config", str(self.settings.build_type)])

        if self.options.shared:
            build_args.append("--build_shared_lib")

        if self.options.parallel:
            build_args.append("--parallel")

        if self.options.with_openmp:
            build_args.append("--use_openmp")

        if self.options.with_dnnl:
            build_args.append("--use_dnnl")

        if self.options.with_nnapi:
            build_args.append("--use_nnapi")

        if self.options.with_winml:
            build_args.append("--use_winml")

        if self.options.with_dml:
            build_args.append("--use_dml")

        if self.options.with_python_wheel:
            build_args.append("--build_wheel")

        if self.options.with_csharp:
            build_args.append("--build_csharp")

        if self.options.with_java:
            build_args.append("--use_java")

        if self.options.with_tests:
            build_args.append("--tests")
        else:
            build_args.append("--skip_tests")

        build_args.extend([
            "--cmake_extra_defines",
            f"CMAKE_INSTALL_PREFIX={self.package_folder}"
        ])

        # TODO full list of options in
        # https://github.com/microsoft/onnxruntime/blob/master/BUILD.md

        if self.settings.os == "Android":
            build_args.append("--android")

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

            build_args.extend(["--android_sdk_path", android_sdk_root])
            build_args.extend(["--android_ndk_path", android_ndk_root])
            build_args.extend([
                "--android_abi",
                tools.to_android_abi(self.settings.arch)
            ])

            if self.settings.os.api_level:
                build_args.extend([
                    "--android_api", str(self.settings.os.api_level)
                ])

        with tools.chdir(self._source_subfolder):
            self.run(" ".join([build_script] + build_args))

    def package(self):
        build_dir = self._onnxruntime_build_dir
        self.run(f"cmake --build {build_dir} --target install")

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
