from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, rmdir
import os

required_conan_version = ">=1.60.0 <2.0 || >=2.0.8"

class OpenvinoConan(ConanFile):
    name = "openvino"

    # Optional metadata
    license = "Apache-2.0"
    homepage = "https://github.com/openvinotoolkit/openvino"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Open Visual Inference And Optimization toolkit for AI inference"
    topics = ("nlp", "natural-language-processing", "ai", "computer-vision", "deep-learning", "transformers", "inference",
              "speech-recognition", "yolo", "performance-boost", "diffusion-models", "recomendation-system", "stable-diffusion",
              "generative-ai", "llm-inference", "optimize-ai", "deploy-ai")
    package_id_non_embed_mode = "patch_mode"
    short_paths = True

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
    options_description = {
        "shared": "Builds OpenVINO as shared libraries",
        "fPIC": "Enables / Disables the -fPIC option. Only valid for shared=True",
        # HW plugins
        "enable_cpu": "Builds CPU plugin",
        "enable_gpu": "Builds GPU plugin",
        # SW plugins
        "enable_auto": "Builds AUTO plugin",
        "enable_hetero": "Builds HETERO plugin",
        "enable_auto_batch": "Builds BATCH plugin",
        # Frontends
        "enable_ir_frontend": "Builds IR frontend",
        "enable_onnx_frontend": "Builds ONNX frontend",
        "enable_tf_frontend": "Builds TensorFlow frontend",
        "enable_tf_lite_frontend": "Builds TensorFlow Lite frontend",
        "enable_paddle_frontend": "Builds PaddlePaddle frontend",
        "enable_pytorch_frontend": "Builds PyTorch frontend"
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
    def _gna_option_available(self):
        return (self.settings.os == "Linux" or self.settings.os == "Windows") and \
            self._target_x86_64 and Version(self.version) < "2024.0.0"

    @property
    def _gpu_option_available(self):
        return self.settings.os != "Macos" and self._target_x86_64

    @property
    def _preprocessing_available(self):
        return Version(self.version) <= "2023.1.0"

    def source(self):
        # pass
        get(self, **self.conan_data["sources"][self.version]["openvino"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["onednn_cpu"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/onednn")
        get(self, **self.conan_data["sources"][self.version]["mlas"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/mlas")
        get(self, **self.conan_data["sources"][self.version]["arm_compute"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/ComputeLibrary")
        get(self, **self.conan_data["sources"][self.version]["onednn_gpu"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_gpu/thirdparty/onednn_gpu")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._gpu_option_available:
            del self.options.enable_gpu

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self._protobuf_required:
            # static build + TF FE requires full protobuf, otherwise we can use lite version
            # self.options['protobuf'].lite = True # self.options.shared or not self.options.enable_tf_frontend
            if self.options.shared:
                # we need to use static protobuf to overcome potential issues with multiple registrations inside
                # protobuf when frontends (implemented as plugins) are loaded multiple times in runtime
                # self.options['protobuf'].shared = False
                pass
        if self.options.enable_tf_lite_frontend:
            # only flatc is required for TF Lite FE plus headers
            # self.options['flatbuffers'].header_only = True
            pass

    def build_requirements(self):
        if self._target_arm:
            self.tool_requires("scons/[>=4.2.0]")
        if cross_building(self):
            if self._protobuf_required:
                self.tool_requires("protobuf/<host_version>")
            if self.options.enable_tf_lite_frontend:
                self.tool_requires("flatbuffers/<host_version>")
        if not self.options.shared:
            self.tool_requires("cmake/[>=3.18]")

    def requirements(self):
        self.requires("onetbb/2021.3.0")
        self.requires("pugixml/[>=1.10]")
        if self._target_x86_64:
            self.requires("xbyak/6.62")
        if self.options.get_safe("enable_gpu"):
            self.requires("opencl-headers/2023.04.17")
            self.requires("opencl-clhpp-headers/2023.04.17")
            self.requires("opencl-icd-loader/2023.04.17")
        if self._protobuf_required:
            self.requires("protobuf/3.21.9")
        if self.options.enable_tf_frontend:
            self.requires("snappy/[>=1.1.7]")
        if self.options.enable_onnx_frontend:
            self.requires("onnx/1.13.1")
        if self.options.enable_tf_lite_frontend:
            self.requires("flatbuffers/22.9.24")
        if self._preprocessing_available:
            self.requires("ade/0.1.2a")

    def layout(self):
        cmake_layout(self, src_folder="src")
        # cmake_layout(self, src_folder="/Users/sandye51/Documents/Programming/git_repo/openvino",
        #                    build_folder="/Users/sandye51/Documents/Programming/builds/openvino-release-conan")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        # HW plugins
        toolchain.cache_variables["ENABLE_INTEL_CPU"] = self.options.enable_cpu
        if self._gpu_option_available:
            toolchain.cache_variables["ENABLE_INTEL_GPU"] = self.options.enable_gpu
            toolchain.cache_variables["ENABLE_ONEDNN_FOR_GPU"] = False
            # toolchain.cache_variables["ENABLE_ONEDNN_FOR_GPU"] = self.options.shared or not self.options.enable_cpu
        if self._gna_option_available:
            toolchain.cache_variables["ENABLE_INTEL_GNA"] = False
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
        # Dependencies
        toolchain.cache_variables["ENABLE_SYSTEM_TBB"] = True
        # toolchain.cache_variables["ENABLE_TBBBIND_2_5"] = self.options["onetbb"].shared
        toolchain.cache_variables["ENABLE_TBBBIND_2_5"] = self.options.shared
        toolchain.cache_variables["ENABLE_SYSTEM_PUGIXML"] = True
        if self._protobuf_required:
            toolchain.cache_variables["ENABLE_SYSTEM_PROTOBUF"] = True
        if self.options.enable_tf_frontend:
            toolchain.cache_variables["ENABLE_SYSTEM_SNAPPY"] = True
        if self.options.enable_tf_lite_frontend:
            toolchain.cache_variables["ENABLE_SYSTEM_FLATBUFFERS"] = True
        # misc
        if self._preprocessing_available:
            toolchain.cache_variables["ENABLE_GAPI_PREPROCESSING"] = True
        toolchain.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        toolchain.cache_variables["CPACK_GENERATOR"] = "CONAN"
        toolchain.cache_variables["ENABLE_PROFILING_ITT"] = False
        toolchain.cache_variables["ENABLE_PYTHON"] = False
        toolchain.cache_variables["ENABLE_WHEEL"] = False
        toolchain.cache_variables["ENABLE_CPPLINT"] = False
        toolchain.cache_variables["ENABLE_NCC_STYLE"] = False
        toolchain.cache_variables["ENABLE_SAMPLES"] = False
        toolchain.cache_variables["ENABLE_TEMPLATE"] = False
        # toolchain.cache_variables["CMAKE_CXX_COMPILER_LAUNCHER"] = "ccache"
        # toolchain.cache_variables["CMAKE_C_COMPILER_LAUNCHER"] = "ccache"
        toolchain.generate()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # generic OpenVINO requirements
            check_min_cppstd(self, "11")
        #     if self.options.enable_cpu:
        #         # MLAS requires C++ 17
        #         check_min_cppstd(self, "17")
        if self.options.enable_cpu and self.options.get_safe("enable_gpu") and not self.options.shared:
            # GPU and CPU are mutually exclusive in static build configuration
            raise ConanInvalidConfiguration(f"{self.ref} cannot build both CPU and GPU in static build. Please, select the only plugin.")
        if self.settings.os == "Emscripten":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Emscripten")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

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

        openvino_runtime = self.cpp_info.components["Runtime"]
        openvino_runtime.set_property("cmake_target_name", "openvino::runtime")
        openvino_runtime.libs = ["openvino", "openvino_c"]
        openvino_runtime.requires = ["onetbb::onetbb", "pugixml::pugixml"]
        if self._preprocessing_available:
            openvino_runtime.requires.append("ade::ade")
        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            openvino_runtime.system_libs = ["m", "dl", "pthread"]
        if self.settings.os == "Windows":
            openvino_runtime.system_libs.append("shlwapi")

        # Have to expose all internal libraries for static libraries case
        if not self.options.shared:
            openvino_runtime.libs.extend(["openvino_reference", "openvino_itt",
                                          "openvino_util", "openvino_builders",
                                          "openvino_shape_inference"])
            if self._preprocessing_available:
                openvino_runtime.libs.extend(["openvino_gapi_preproc", "fluid"])
            # HW plugins
            if self.options.enable_cpu:
                openvino_runtime.libs.extend(["openvino_onednn_cpu", "openvino_snippets", "mlas"])
                if self._target_arm:
                    openvino_runtime.libs.extend(["openvino_arm_cpu_plugin", "arm_compute-static"])
                else:
                    openvino_runtime.libs.extend(["openvino_intel_cpu_plugin"])
            if self.options.get_safe("enable_gpu"):
                openvino_runtime.libs.extend(["openvino_intel_gpu_plugin", "openvino_intel_gpu_runtime",
                                              "openvino_intel_gpu_kernels", "openvino_intel_gpu_graph"])
            # SW plugins
            if self.options.enable_auto:
                openvino_runtime.libs.append("openvino_auto_plugin")
            if self.options.enable_hetero:
                openvino_runtime.libs.append("openvino_hetero_plugin")
            if self.options.enable_auto_batch:
                openvino_runtime.libs.append("openvino_auto_batch_plugin")
            # Frontends
            if self.options.enable_ir_frontend:
                openvino_runtime.libs.append("openvino_ir_frontend")
            if self.options.enable_onnx_frontend:
                openvino_runtime.libs.extend(["openvino_onnx_frontend", "onnx_common"])
                openvino_runtime.requires.extend(["protobuf::libprotobuf", "onnx::onnx"])
            if self.options.enable_tf_frontend:
                openvino_runtime.libs.extend(["openvino_tensorflow_common", "openvino_tensorflow_frontend"])
                openvino_runtime.requires.extend(["protobuf::libprotobuf", "snappy::snappy"])
            if self.options.enable_tf_lite_frontend:
                openvino_runtime.libs.extend(["openvino_tensorflow_common", "openvino_tensorflow_lite_frontend"])
                openvino_runtime.requires.extend(["flatbuffers::flatbuffers"])
            if self.options.enable_paddle_frontend:
                openvino_runtime.libs.append("openvino_paddle_frontend")
                openvino_runtime.requires.append("protobuf::libprotobuf")
            if self.options.enable_pytorch_frontend:
                openvino_runtime.libs.append("openvino_pytorch_frontend")

        if self.options.enable_onnx_frontend:
            openvino_onnx = self.cpp_info.components["ONNX"]
            openvino_onnx.set_property("cmake_target_name", "openvino::frontend::onnx")
            openvino_onnx.libs = ["openvino_onnx_frontend"]
            openvino_onnx.requires = ["Runtime", "onnx::onnx", "protobuf::libprotobuf"]
            if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
                openvino_onnx.system_libs = ["m", "dl", "pthread"]

        if self.options.enable_paddle_frontend:
            openvino_paddle = self.cpp_info.components["Paddle"]
            openvino_paddle.set_property("cmake_target_name", "openvino::frontend::paddle")
            openvino_paddle.libs = ["openvino_paddle_frontend"]
            openvino_paddle.requires = ["Runtime", "protobuf::libprotobuf"]
            if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
                openvino_paddle.system_libs = ["m", "dl", "pthread"]

        if self.options.enable_tf_frontend:
            openvino_tensorflow = self.cpp_info.components["TensorFlow"]
            openvino_tensorflow.set_property("cmake_target_name", "openvino::frontend::tensorflow")
            openvino_tensorflow.libs = ["openvino_tensorflow_frontend"]
            openvino_tensorflow.requires = ["Runtime", "protobuf::libprotobuf", "snappy::snappy"]
            if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
                openvino_onnx.system_libs = ["m", "dl", "pthread"]

        if self.options.enable_pytorch_frontend:
            openvino_pytorch = self.cpp_info.components["PyTorch"]
            openvino_pytorch.set_property("cmake_target_name", "openvino::frontend::pytorch")
            openvino_pytorch.libs = ["openvino_pytorch_frontend"]
            openvino_pytorch.requires = ["Runtime"]
            if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
                openvino_onnx.system_libs = ["m", "dl", "pthread"]

        if self.options.enable_tf_lite_frontend:
            openvino_tensorflow_lite = self.cpp_info.components["TensorFlowLite"]
            openvino_tensorflow_lite.set_property("cmake_target_name", "openvino::frontend::tensorflow_lite")
            openvino_tensorflow_lite.libs = ["openvino_tensorflow_lite_frontend"]
            # TODO: try to remove flatbuffers from 'requires', because only headers are used privately
            openvino_tensorflow_lite.requires = ["Runtime", "flatbuffers::flatbuffers"]
            if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
                openvino_onnx.system_libs = ["m", "dl", "pthread"]
