from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=2.1"


class OpenvinoConan(ConanFile):
    name = "openvino"

    license = "Apache-2.0"
    homepage = "https://github.com/openvinotoolkit/openvino"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Open Visual Inference And Optimization toolkit for AI inference"
    topics = ("nlp", "natural-language-processing", "ai", "computer-vision", "deep-learning", "transformers", "inference",
              "speech-recognition", "yolo", "performance-boost", "diffusion-models", "recommendation-system", "stable-diffusion",
              "generative-ai", "llm-inference", "optimize-ai", "deploy-ai")
    package_id_non_embed_mode = "patch_mode"
    package_type = "library"
    no_copy_source = True

    # Binary configuration
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # HW plugins
        "enable_cpu": [True, False],
        "enable_gpu": [True, False],
        # SW plugins
        "enable_auto": [True, False],
        "enable_hetero": [True, False],
        "enable_auto_batch": [True, False],
        # Frontends
        "enable_ir_frontend": [True, False],
        "enable_onnx_frontend": [True, False],
        "enable_tf_frontend": [True, False],
        "enable_tf_lite_frontend": [True, False],
        "enable_paddle_frontend": [True, False],
        "enable_pytorch_frontend": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # HW plugins
        "enable_cpu": True,
        "enable_gpu": True,
        # SW plugins
        "enable_auto": True,
        "enable_hetero": True,
        "enable_auto_batch": True,
        # Frontends
        "enable_ir_frontend": True,
        "enable_onnx_frontend": True,
        "enable_tf_frontend": True,
        "enable_tf_lite_frontend": True,
        "enable_paddle_frontend": True,
        "enable_pytorch_frontend": True
    }

    @property
    def _protobuf_required(self):
        return self.options.enable_tf_frontend or self.options.enable_onnx_frontend or self.options.enable_paddle_frontend

    @property
    def _target_arm(self):
        return "arm" in self.settings.arch

    @property
    def _target_x86_64(self):
        return self.settings.arch == "x86_64"

    @property
    def _npu_option_available(self):
        return self.settings.os in ["Linux", "Windows"] and self._target_x86_64

    @property
    def _gpu_option_available(self):
        return self.settings.os != "Macos" and self._target_x86_64

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["openvino"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["onednn_cpu"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/onednn")
        get(self, **self.conan_data["sources"][self.version]["mlas"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/mlas")
        get(self, **self.conan_data["sources"][self.version]["arm_compute"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/ComputeLibrary")
        get(self, **self.conan_data["sources"][self.version]["onednn_gpu"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_gpu/thirdparty/onednn_gpu")
        get(self, **self.conan_data["sources"][self.version]["arm_kleidiai"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/kleidiai")
        rmdir(self, f"{self.source_folder}/src/plugins/intel_gpu/thirdparty/rapidjson")
        apply_conandata_patches(self)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._gpu_option_available:
            del self.options.enable_gpu

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            if self._protobuf_required:
                # even though OpenVINO can work with dynamic protobuf, it's still recommended to use static
                self.options["protobuf"].shared = False

    def build_requirements(self):
        if self._target_arm:
            self.tool_requires("scons/4.3.0")
        if self._protobuf_required:
            self.tool_requires("protobuf/<host_version>")
        if self.options.enable_tf_lite_frontend:
            self.tool_requires("flatbuffers/<host_version>")
        self.tool_requires("cmake/[>=3.18 <4]")

    def requirements(self):
        self.requires("onetbb/2021.10.0")
        self.requires("pugixml/1.14")
        self.requires("nlohmann_json/3.11.3")
        if self._target_x86_64:
            self.requires("xbyak/6.73")
        if self.options.get_safe("enable_gpu"):
            self.requires("opencl-icd-loader/2023.04.17")
            self.requires("rapidjson/cci.20220822")
        if self._protobuf_required:
            self.requires("protobuf/3.21.12")
        if self.options.enable_tf_frontend:
            self.requires("snappy/1.1.10")
        if self.options.enable_onnx_frontend:
            self.requires("onnx/1.20.0")
        if self.options.enable_tf_lite_frontend:
            self.requires("flatbuffers/23.5.26")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        # HW plugins
        toolchain.cache_variables["ENABLE_INTEL_CPU"] = self.options.enable_cpu
        if self._gpu_option_available:
            toolchain.cache_variables["ENABLE_INTEL_GPU"] = self.options.enable_gpu
            toolchain.cache_variables["ENABLE_ONEDNN_FOR_GPU"] = (
                self.options.enable_gpu
                or not self.options.enable_cpu
                or self.options.shared
            )
        if self._npu_option_available:
            toolchain.cache_variables["ENABLE_INTEL_NPU"] = False
        # SW plugins
        toolchain.cache_variables["ENABLE_AUTO"] = self.options.enable_auto
        toolchain.cache_variables["ENABLE_MULTI"] = self.options.enable_auto
        toolchain.cache_variables["ENABLE_AUTO_BATCH"] = self.options.enable_auto_batch
        toolchain.cache_variables["ENABLE_HETERO"] = self.options.enable_hetero
        # Frontends
        toolchain.cache_variables["ENABLE_OV_IR_FRONTEND"] = self.options.enable_ir_frontend
        toolchain.cache_variables["ENABLE_OV_PADDLE_FRONTEND"] = self.options.enable_paddle_frontend
        toolchain.cache_variables["ENABLE_OV_TF_FRONTEND"] = self.options.enable_tf_frontend
        toolchain.cache_variables["ENABLE_OV_TF_LITE_FRONTEND"] = self.options.enable_tf_lite_frontend
        toolchain.cache_variables["ENABLE_OV_ONNX_FRONTEND"] = self.options.enable_onnx_frontend
        toolchain.cache_variables["ENABLE_OV_PYTORCH_FRONTEND"] = self.options.enable_pytorch_frontend
        toolchain.cache_variables["ENABLE_OV_JAX_FRONTEND"] = False
        # Dependencies
        toolchain.cache_variables["ENABLE_SYSTEM_TBB"] = True
        toolchain.cache_variables["ENABLE_TBBBIND_2_5"] = False
        toolchain.cache_variables["ENABLE_SYSTEM_PUGIXML"] = True
        if self._protobuf_required:
            toolchain.cache_variables["ENABLE_SYSTEM_PROTOBUF"] = True
        if self.options.enable_tf_frontend:
            toolchain.cache_variables["ENABLE_SYSTEM_SNAPPY"] = True
        if self.options.enable_tf_lite_frontend:
            toolchain.cache_variables["ENABLE_SYSTEM_FLATBUFFERS"] = True
        if self.options.get_safe("enable_gpu"):
            toolchain.cache_variables["ENABLE_SYSTEM_OPENCL"] = True
        # misc
        toolchain.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        toolchain.cache_variables["CPACK_GENERATOR"] = "CONAN"
        toolchain.cache_variables["ENABLE_PROFILING_ITT"] = False
        toolchain.cache_variables["ENABLE_PYTHON"] = False
        toolchain.cache_variables["ENABLE_PROXY"] = False
        toolchain.cache_variables["ENABLE_WHEEL"] = False
        toolchain.cache_variables["ENABLE_CPPLINT"] = False
        toolchain.cache_variables["ENABLE_NCC_STYLE"] = False
        toolchain.cache_variables["ENABLE_SAMPLES"] = False
        toolchain.cache_variables["ENABLE_TEMPLATE"] = False
        if self.settings.os == "Macos":
            toolchain.cache_variables["OV_FORCE_ADHOC_SIGN"] = True
        toolchain.generate()

    def validate_build(self):
        check_min_cppstd(self, 17)

        # OpenVINO has unresolved symbols, when clang is used with libc++
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration(
                f"{self.ref} cannot be built with clang and libc++ due to unresolved symbols. "
                f"Please, use libstdc++ instead."
            )

        if self.settings.os == "Emscripten":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Emscripten")

        # Failing on Conan Center CI due to memory usage
        if os.getenv("CONAN_CENTER_BUILD_SERVICE") and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Debug build type on Conan Center CI")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        for target in ["ov_frontends", "ov_plugins", "openvino_c"]:
            cmake.build(target=target)

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # remove cmake and .pc files, since they will be generated later by Conan itself in package_info()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.set_property("cmake_file_name", "OpenVINO")
        self.cpp_info.set_property("pkg_config_name", "openvino")

        lib_suffix = ""
        if self.settings.build_type == "Debug" and self.settings.os in ("Windows", "Macos"):
            lib_suffix = "d"

        openvino_runtime = self.cpp_info.components["Runtime"]
        openvino_runtime.set_property("cmake_target_name", "openvino::runtime")
        openvino_runtime.requires = ["onetbb::libtbb", "pugixml::pugixml"]
        openvino_runtime.requires.append("nlohmann_json::nlohmann_json")
        openvino_runtime.libs = [f"openvino{lib_suffix}"]
        if self._target_x86_64:
            openvino_runtime.requires.append("xbyak::xbyak")
        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            openvino_runtime.system_libs = ["m", "dl", "pthread"]
        if self.settings.os == "Windows":
            openvino_runtime.system_libs.append("shlwapi")

        # Have to expose all internal libraries for static libraries case
        if not self.options.shared:
            # HW plugins
            if self.options.enable_cpu:
                openvino_runtime.libs.append(f"openvino_arm_cpu_plugin{lib_suffix}" if self._target_arm else f"openvino_intel_cpu_plugin{lib_suffix}")
                openvino_runtime.libs.extend([f"openvino_onednn_cpu{lib_suffix}", f"openvino_snippets{lib_suffix}", f"mlas{lib_suffix}"])
                openvino_runtime.libs.append(f"openvino_xml_util{lib_suffix}")
                if self._target_arm:
                    openvino_runtime.libs.append("arm_compute-static")
                    openvino_runtime.libs.append(f"kleidiai{lib_suffix}")
            if self.options.get_safe("enable_gpu"):
                openvino_runtime.libs.extend([
                    f"openvino_intel_gpu_plugin{lib_suffix}",
                    f"openvino_intel_gpu_graph{lib_suffix}",
                    f"openvino_intel_gpu_runtime{lib_suffix}",
                    f"openvino_intel_gpu_kernels{lib_suffix}"
                ])
                if not self.options.enable_cpu:
                    openvino_runtime.libs.append(f"openvino_onednn_gpu{lib_suffix}")
            # SW plugins
            if self.options.enable_auto:
                openvino_runtime.libs.append(f"openvino_auto_plugin{lib_suffix}")
            if self.options.enable_hetero:
                openvino_runtime.libs.append(f"openvino_hetero_plugin{lib_suffix}")
            if self.options.enable_auto_batch:
                openvino_runtime.libs.append(f"openvino_auto_batch_plugin{lib_suffix}")
            # Frontends
            if self.options.enable_ir_frontend:
                openvino_runtime.libs.append(f"openvino_ir_frontend{lib_suffix}")
            if self.options.enable_onnx_frontend:
                openvino_runtime.libs.extend([f"openvino_onnx_frontend{lib_suffix}", f"openvino_onnx_common{lib_suffix}"])
                openvino_runtime.requires.extend(["protobuf::libprotobuf", "onnx::onnx"])
            if self.options.enable_tf_frontend:
                openvino_runtime.libs.extend([f"openvino_tensorflow_frontend{lib_suffix}"])
                openvino_runtime.requires.extend(["protobuf::libprotobuf", "snappy::snappy"])
            if self.options.enable_tf_lite_frontend:
                openvino_runtime.libs.extend([f"openvino_tensorflow_lite_frontend{lib_suffix}"])
                openvino_runtime.requires.extend(["flatbuffers::flatbuffers"])
            if self.options.enable_tf_frontend or self.options.enable_tf_lite_frontend:
                openvino_runtime.libs.extend([f"openvino_tensorflow_common{lib_suffix}"])
            if self.options.enable_paddle_frontend:
                openvino_runtime.libs.append(f"openvino_paddle_frontend{lib_suffix}")
                openvino_runtime.requires.append("protobuf::libprotobuf")
            if self.options.enable_pytorch_frontend:
                openvino_runtime.libs.append(f"openvino_pytorch_frontend{lib_suffix}")
            # Common private dependencies should go last, because they satisfy dependencies for all other libraries
            openvino_runtime.libs.extend([
                f"openvino_reference{lib_suffix}",
                f"openvino_shape_inference{lib_suffix}",
                f"openvino_itt{lib_suffix}",
                # utils goes last since all others depend on it
                f"openvino_util{lib_suffix}",
                f"openvino_common_translators{lib_suffix}"
            ])

            # set 'openvino' once again for transformations objects files (cyclic dependency)
            # openvino_runtime.libs.append("openvino")
            full_openvino_lib_path = os.path.join(self.package_folder, "lib", f"openvino{lib_suffix}.lib").replace("\\", "/") if self.settings.os == "Windows" else \
                                     os.path.join(self.package_folder, "lib", f"libopenvino{lib_suffix}.a")
            openvino_runtime.system_libs.insert(0, full_openvino_lib_path)
            # Add definition to prevent symbols importing
            openvino_runtime.defines = ["OPENVINO_STATIC_LIBRARY"]
        if self.options.get_safe("enable_gpu"):
            openvino_runtime.requires.extend(["opencl-icd-loader::opencl-icd-loader", "rapidjson::rapidjson"])
            if self.settings.os == "Windows":
                openvino_runtime.system_libs.append("setupapi")

        openvino_runtime_c = self.cpp_info.components["Runtime_C"]
        openvino_runtime_c.set_property("cmake_target_name", "openvino::runtime::c")
        openvino_runtime_c.libs = [f"openvino_c{lib_suffix}"]
        openvino_runtime_c.requires = ["Runtime"]

        if self.options.enable_onnx_frontend:
            openvino_onnx = self.cpp_info.components["ONNX"]
            openvino_onnx.set_property("cmake_target_name", "openvino::frontend::onnx")
            openvino_onnx.libs = [f"openvino_onnx_frontend{lib_suffix}"]
            openvino_onnx.requires = ["Runtime", "onnx::onnx", "protobuf::libprotobuf"]

        if self.options.enable_paddle_frontend:
            openvino_paddle = self.cpp_info.components["Paddle"]
            openvino_paddle.set_property("cmake_target_name", "openvino::frontend::paddle")
            openvino_paddle.libs = [f"openvino_paddle_frontend{lib_suffix}"]
            openvino_paddle.requires = ["Runtime", "protobuf::libprotobuf"]

        if self.options.enable_tf_frontend:
            openvino_tensorflow = self.cpp_info.components["TensorFlow"]
            openvino_tensorflow.set_property("cmake_target_name", "openvino::frontend::tensorflow")
            openvino_tensorflow.libs = [f"openvino_tensorflow_frontend{lib_suffix}"]
            openvino_tensorflow.requires = ["Runtime", "protobuf::libprotobuf", "snappy::snappy"]

        if self.options.enable_pytorch_frontend:
            openvino_pytorch = self.cpp_info.components["PyTorch"]
            openvino_pytorch.set_property("cmake_target_name", "openvino::frontend::pytorch")
            openvino_pytorch.libs = [f"openvino_pytorch_frontend{lib_suffix}"]
            openvino_pytorch.requires = ["Runtime"]

        if self.options.enable_tf_lite_frontend:
            openvino_tensorflow_lite = self.cpp_info.components["TensorFlowLite"]
            openvino_tensorflow_lite.set_property("cmake_target_name", "openvino::frontend::tensorflow_lite")
            openvino_tensorflow_lite.libs = [f"openvino_tensorflow_lite_frontend{lib_suffix}"]
            openvino_tensorflow_lite.requires = ["Runtime", "flatbuffers::flatbuffers"]
