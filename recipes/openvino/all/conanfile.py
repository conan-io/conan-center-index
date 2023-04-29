from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.cmake import CMake
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, rename, rmdir
import os

class OpenvinoConan(ConanFile):
    name = "openvino"

    # Optional metadata
    license = "Apache-2.0"
    author = "Intel Corporation"
    homepage = "https://docs.openvino.ai/latest/home.html"
    url = "https://github.com/openvinotoolkit/openvino"
    description = "Open Visual Inference And Optimization toolkit for AI inference"
    topics = ("deep-learning", "artificial-intelligence", "performance" "inference-engine", "openvino")

    # Binary configuration
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True
    }
    # TODO:
    # generators = ["CMakeToolchain", "CMakeDeps"]

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = ("*")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["openvino"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["onednn_cpu"], strip_root=True,
            destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/onednn")
        get(self, **self.conan_data["sources"][self.version]["ittapi"], strip_root=True,
            destination=f"{self.source_folder}/thirdparty/ittapi/ittapi")
        get(self, **self.conan_data["sources"][self.version]["xbyak"], strip_root=True,
            destination=f"{self.source_folder}/thirdparty/xbyak")
        get(self, **self.conan_data["sources"][self.version]["onnx"], strip_root=True,
            destination=f"{self.source_folder}/thirdparty/onnx/onnx")
        # TODO:
        # if "arm" in self.settings.arch:
        if True:
            if Version(self.version) <= "2022.3.0":
                get(self, **self.conan_data["sources"][self.version]["openvino_contrib"], strip_root=True,
                    destination=f"{self.source_folder}/openvino_contrib")
                get(self, **self.conan_data["sources"][self.version]["arm_compute"], strip_root=True,
                    destination=f"{self.source_folder}/openvino_contrib/modules/arm_plugin/thirdparty/ComputeLibrary")
            else:
                get(self, **self.conan_data["sources"][self.version]["arm_compute"], strip_root=True,
                    destination=f"{self.source_folder}/src/plugins/intel_cpu/thirdparty/ComputeLibrary")

    def build_requirements(self):
        # TODO: fix scons recipe
        # if "arm" in self.settings.arch:
        #     self.build_requires("scons/[>=4.2.0]")
        self.build_requires("protobuf/[>=3.21.9]")

    # TODO: specify minimal cxxstd version and compiler versions

    def requirements(self):
        self.requires("ade/0.1.2a")
        self.requires("onetbb/[>=2021.2.1]")
        self.requires("pugixml/[>=1.10]")
        self.requires("protobuf/[>=3.18.2]")
        self.requires("flatbuffers/[>=22.9.24]")
        self.requires("xbyak/6.62") # TODO: this dependency is not used right now

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # TODO: why do we need it ?
        # self.options['onetbb'].tbbmalloc = True
        # self.options['onetbb'].shared = False
        self.options['protobuf'].lite = True

    def configure(self):
        if self.options.get_safe("shared", True):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        toolchain = CMakeToolchain(self)
        # mapping conan options to cmake variables
        toolchain.cache_variables["BUILD_SHARED_LIBS"] = self.options.get_safe("shared", True)
        toolchain.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        # plugins
        toolchain.cache_variables["ENABLE_INTEL_CPU"] = "ON"
        toolchain.cache_variables["ENABLE_INTEL_GPU"] = "OFF"
        toolchain.cache_variables["ENABLE_TEMPLATE"] = "OFF"
        toolchain.cache_variables["ENABLE_INTEL_GNA"] = "OFF"
        if Version(self.version) <= "2022.3.0":
            toolchain.cache_variables["ENABLE_INTEL_MYRIAD_COMMON"] = "OFF"
        if "arm" in self.settings.arch and Version(self.version) <= "2022.3.0":
            toolchain.cache_variables["OPENVINO_EXTRA_MODULES"] = f"{self.source_folder}/openvino_contrib/modules/arm_plugin"
        # frontends
        toolchain.cache_variables["ENABLE_OV_PADDLE_FRONTEND"] = "ON"
        toolchain.cache_variables["ENABLE_OV_TF_FRONTEND"] = "OFF"
        toolchain.cache_variables["ENABLE_OV_ONNX_FRONTEND"] = "OFF"
        # misc
        toolchain.cache_variables["CPACK_GENERATOR"] = "BREW"
        toolchain.cache_variables["ENABLE_SAMPLES"] = "OFF"
        toolchain.cache_variables["ENABLE_GAPI_PREPROCESSING"] = "OFF"
        toolchain.cache_variables["ENABLE_COMPILE_TOOL"] = "OFF"
        toolchain.cache_variables["ENABLE_PYTHON"] = "OFF"
        toolchain.cache_variables["ENABLE_CPPLINT"] = "OFF"
        toolchain.cache_variables["ENABLE_NCC_STYLE"] = "OFF"
        toolchain.cache_variables["CMAKE_CXX_COMPILER_LAUNCHER"] = "ccache"
        toolchain.cache_variables["CMAKE_C_COMPILER_LAUNCHER"] = "ccache"
        # dependencies
        toolchain.cache_variables["ENABLE_SYSTEM_TBB"] = "ON"
        toolchain.cache_variables["ENABLE_SYSTEM_PUGIXML"] = "ON"
        toolchain.cache_variables["ENABLE_SYSTEM_PROTOBUF"] = "ON"
        if Version(self.version) >= "2023.0.0":
            toolchain.cache_variables["ENABLE_SYSTEM_SNAPPY"] = "ON"
            toolchain.cache_variables["ENABLE_SYSTEM_FLATBUFFERS"] = "ON"
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        # install only required components
        for comp in ["core", "core_dev", "licensing"
                     "cpu", "gpu", "batch", "multi", "hetero",
                     "ir", "onnx", "paddle", "pytorch", "tensorflow", "tensorflow_lite"]:
            cmake.install(component=comp)
        # move liceneses to a conan usual location
        rename(self, os.path.join(self.package_folder, "share", "doc", f"openvino-${self.version}"),
            os.path.join(self.package_folder, "licenses"))
        # remove cmake and pkg-config files, since they later will generated by conan itself in package_info()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenVINO")
        self.cpp_info.set_property("pkg_config_name", "openvino")

        openvino_runtime = self.cpp_info.components["Runtime"]
        openvino_runtime.set_property("cmake_target_name", "openvino::runtime")
        openvino_runtime.libs = ["openvino", "openvino_c"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            openvino_runtime.system_libs = ["m", "dl", "rt", "pthread"]
        # TODO: add dependency on TBB, pugixml
        # openvino_runtime.requires = ["TBB::tbb", "pugixml"]

        # TODO: add more components like frontends
