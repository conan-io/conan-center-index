from conan import ConanFile
from conan.tools.build import can_run, check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import rmdir
from conan.tools.scm import Version
import os

# we need 2.0.5 because of <host_version> placeholder
required_conan_version = ">=2.0.5"

class OpenvinoConan(ConanFile):
    name = "openvino"

    license = "Apache-2.0"
    author = "Intel Corporation"
    homepage = "https://docs.openvino.ai/latest/home.html"
    url = "https://github.com/openvinotoolkit/openvino"
    description = "Open Visual Inference And Optimization toolkit for AI inference"
    topics = ("deep-learning", "deeplearning", "artificialintelligenceai", "artificial-intelligence", 
              "performance", "datamining", "neuralnetwork", "inference-engine")
    version = "2023.1.0"

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
        # frontends
        "enable_ir_frontend": [True, False],
        "enable_onnx_frontend": [True, False],
        "enable_tf_frontend": [True, False],
        "enable_tf_lite_frontend": [True, False],
        "enable_pdpd_frontend": [True, False],
        "enable_pytorch_frontend": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        # HW plugins
        "enable_cpu": True,
        "enable_gpu": True,
        # SW plugins
        "enable_auto": True,
        "enable_hetero": True,
        "enable_auto_batch": True,
        # frontends
        "enable_ir_frontend": True,
        "enable_onnx_frontend": True,
        "enable_tf_frontend": True,
        "enable_tf_lite_frontend": True,
        "enable_pdpd_frontend": True,
        "enable_pytorch_frontend": True
    }

    # TODO: understand what to export
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = ("*")

    @property
    def _protobuf_required(self):
        return self.options.enable_tf_frontend or self.options.enable_onnx_frontend or self.options.enable_pdpd_frontend

    @property
    def _target_arm(self):
        return "arm" in self.settings.arch

    @property
    def _target_x86_64(self):
        return self.settings.arch == "x86_64"

    @property
    def _gpu_option_available(self):
        return self.settings.os != "Macos" and self._target_x86_64

    def source(self):
        # get(self, **self.conan_data["sources"][self.version]["openvino"], strip_root=True)
        # get(self, **self.conan_data["sources"][self.version]["onednn_cpu"], strip_root=True,
        #     destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/onednn")
        # get(self, **self.conan_data["sources"][self.version]["onednn_gpu"], strip_root=True,
        #     destination=f"{self.source_folder}/src/plugins/intel_gpu/thirdparty/onednn_gpu")
        # get(self, **self.conan_data["sources"][self.version]["arm_compute"], strip_root=True,
        #     destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/ComputeLibrary")
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._gpu_option_available:
            del self.options.enable_gpu

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self._protobuf_required:
            # static build + TF FE requires full protobuf, otherwise lite is enough
            self.options['protobuf'].lite = self.options.shared or not self.options.enable_tf_frontend
            if self.options.shared:
                # we need to use static protobuf to overcome issues with multiple registrations inside protobuf
                # when frontends (implemented as plugins) are loaded multiple times in runtime
                self.options['protobuf'].shared = False
        if self.options.enable_tf_lite_frontend:
            # only flatc is required for TF Lite FE plus headers
            self.options['flatbuffers'].header_only = True

    def build_requirements(self):
        if self._target_arm:
            self.build_requires("scons/[>=4.2.0]")
        if not can_run(self):
            if self._protobuf_required:
                self.tool_requires("protobuf/[>=3.20.3,<4]")
                self.tool_requires("protobuf/<host_version>")
            if self.options.enable_tf_lite_frontend:
                self.build_requires("flatbuffers/[>=22.9.24]")
                self.build_requires("flatbuffers/<host_version>")

    def requirements(self):
        self.requires("ade/0.1.2a")
        self.requires("onetbb/[>=2021.2.1,<2022]")
        self.requires("pugixml/[>=1.10]")
        if self._target_x86_64:
            self.requires("xbyak/6.62")
        if self.options.get_safe("enable_gpu"):
            self.requires("opencl-headers/2022.09.30")
            self.requires("opencl-clhpp-headers/2022.09.30")
            self.requires("opencl-icd-loader/2022.09.30")
        if self._protobuf_required:
            self.requires("protobuf/[>=3.20.3,<4]")
        if self.options.enable_tf_frontend:
            self.requires("snappy/[>=1.1.7]")
        if self.options.enable_onnx_frontend:
            self.requires("onnx/1.13.1")
        if self.options.enable_tf_lite_frontend:
            self.requires("flatbuffers/[>=22.9.24]")

    def layout(self):
        if self.settings.os == "Macos":
            cmake_layout(self, src_folder="/Users/sandye51/Documents/Programming/git_repo/openvino",
                               build_folder="/Users/sandye51/Documents/Programming/builds/openvino-release-conan")
        else:
            cmake_layout(self, src_folder="/openvino",
                               build_folder="/build-conan-x86-64")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        # HW plugins
        toolchain.cache_variables["ENABLE_INTEL_CPU"] = self.options.enable_cpu
        if self._gpu_option_available:
            toolchain.cache_variables["ENABLE_INTEL_GPU"] = self.options.enable_gpu
        # SW plugins
        toolchain.cache_variables["ENABLE_AUTO"] = self.options.enable_auto
        toolchain.cache_variables["ENABLE_MULTI"] = self.options.enable_auto
        toolchain.cache_variables["ENABLE_AUTO_BATCH"] = self.options.enable_auto_batch
        toolchain.cache_variables["ENABLE_HETERO"] = self.options.enable_hetero
        # frontends
        toolchain.cache_variables["ENABLE_OV_IR_FRONTEND"] = self.options.enable_ir_frontend
        toolchain.cache_variables["ENABLE_OV_PADDLE_FRONTEND"] = self.options.enable_pdpd_frontend
        toolchain.cache_variables["ENABLE_OV_TF_FRONTEND"] = self.options.enable_tf_frontend
        toolchain.cache_variables["ENABLE_OV_TF_LITE_FRONTEND"] = self.options.enable_tf_lite_frontend
        toolchain.cache_variables["ENABLE_OV_ONNX_FRONTEND"] = self.options.enable_onnx_frontend
        toolchain.cache_variables["ENABLE_OV_PYTORCH_FRONTEND"] = self.options.enable_pytorch_frontend
        # dependencies
        toolchain.cache_variables["ENABLE_SYSTEM_TBB"] = True
        toolchain.cache_variables["ENABLE_SYSTEM_PUGIXML"] = True
        if self._protobuf_required:
            toolchain.cache_variables["ENABLE_SYSTEM_PROTOBUF"] = True
        if self.options.enable_tf_frontend:
            toolchain.cache_variables["ENABLE_SYSTEM_SNAPPY"] = True
        if self.options.enable_tf_lite_frontend:
            toolchain.cache_variables["ENABLE_SYSTEM_FLATBUFFERS"] = True
        # misc
        if self.options.shared and self.settings.os == "Linux":
            toolchain.cache_variables["ENABLE_LTO"] = True
        if Version(self.version) < "2024.0.0":
            toolchain.cache_variables["ENABLE_INTEL_GNA"] = False
        # if Version(self.version) < "2023.1.0":
        toolchain.cache_variables["ENABLE_COMPILE_TOOL"] = False
        toolchain.cache_variables["CPACK_GENERATOR"] = "CONAN"
        toolchain.cache_variables["ENABLE_PYTHON"] = False
        toolchain.cache_variables["ENABLE_WHEEL"] = False
        toolchain.cache_variables["ENABLE_CPPLINT"] = False
        toolchain.cache_variables["ENABLE_NCC_STYLE"] = False
        toolchain.cache_variables["ENABLE_SAMPLES"] = False
        toolchain.cache_variables["ENABLE_TEMPLATE"] = False
        # REMOVE
        toolchain.cache_variables["CMAKE_CXX_COMPILER_LAUNCHER"] = "ccache"
        toolchain.cache_variables["CMAKE_C_COMPILER_LAUNCHER"] = "ccache"
        toolchain.generate()

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            # generic OpenVINO requirements
            check_min_cppstd(self, "11")
            if self._target_arm and self.options.enable_cpu:
                # ARM Compute Library requires C++ 14
                check_min_cppstd(self, "14")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.set_property("cmake_file_name", "OpenVINO")

        openvino_runtime = self.cpp_info.components["Runtime"]
        openvino_runtime.set_property("cmake_target_name", "openvino::runtime")
        openvino_runtime.libs = ["openvino", "openvino_c"]
        openvino_runtime.requires = ["TBB::tbb"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_runtime.system_libs = ["m", "dl", "rt", "pthread"]

        openvino_onnx_fe = self.cpp_info.components["ONNX"]
        openvino_onnx_fe.set_property("cmake_target_name", "openvino::frontend::onnx")
        openvino_onnx_fe.libs = ["openvino_onnx_frontend"]
        openvino_onnx_fe.requires = ["openvino::Runtime"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_onnx_fe.system_libs = ["m"]

        openvino_pdpd_fe = self.cpp_info.components["Paddle"]
        openvino_pdpd_fe.set_property("cmake_target_name", "openvino::frontend::paddle")
        openvino_pdpd_fe.libs = ["openvino_paddle_frontend"]
        openvino_pdpd_fe.requires = ["openvino::Runtime"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_pdpd_fe.system_libs = ["m"]

        openvino_pytorch_fe = self.cpp_info.components["PyTorch"]
        openvino_pytorch_fe.set_property("cmake_target_name", "openvino::frontend::pytorch")
        openvino_pytorch_fe.libs = ["openvino_pytorch_frontend"]
        openvino_pytorch_fe.requires = ["openvino::Runtime"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_pytorch_fe.system_libs = ["m"]

        openvino_tf_fe = self.cpp_info.components["TensorFlow"]
        openvino_tf_fe.set_property("cmake_target_name", "openvino::frontend::tensorflow")
        openvino_tf_fe.libs = ["openvino_tensorflow_frontend"]
        openvino_tf_fe.requires = ["openvino::Runtime"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_tf_fe.system_libs = ["m"]

        openvino_tf_lite_fe = self.cpp_info.components["TensorFlowLite"]
        openvino_tf_lite_fe.set_property("cmake_target_name", "openvino::frontend::tensorflow_lite")
        openvino_tf_lite_fe.libs = ["openvino_tensorflow_lite_frontend"]
        openvino_tf_lite_fe.requires = ["openvino::Runtime"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_tf_lite_fe.system_libs = ["m"]
