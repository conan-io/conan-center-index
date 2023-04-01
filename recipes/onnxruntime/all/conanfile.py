import os
import re
import shutil
import sys

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conans.errors import ConanInvalidConfiguration, ConanException

required_conan_version = ">=1.53.0"


class ONNXRuntimeConan(ConanFile):
    name = "onnxruntime"
    description = "ONNX Runtime accelerates machine learning across a " \
                  "wide range of frameworks, operating systems, and " \
                  "hardware platforms."
    url = "https://github.com/conan-io/conan-center-index"
    topics = (
        "deep-learning",
        "onnx",
        "neural-networks",
        "machine-learning",
        "ai-framework",
        "hardware-acceleration"
    )
    license = "MIT"
    homepage = "https://onnxruntime.ai"

    exports_sources = ["patches/**"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_coreml": [True, False],
        "with_dml": [True, False],
        "with_cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "with_coreml": False,
        "with_dml": False,
        "with_cuda": False,
        "date/*:use_system_tz_db": True,
        "protobuf/*:lite": True,
        "cpuinfo/*:shared": False,
    }
    # protoc is currently called by onnx without quoting.
    # This breaks on Windows if the username has spaces.
    short_paths = True

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.with_dml
        if not is_apple_os(self):
            del self.options.with_coreml
        if is_apple_os(self):
            del self.options.with_cuda

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("nsync/1.25.0")
        self.requires("abseil/20230125.1")
        self.requires("cpuinfo/cci.20220228")
        self.requires("protobuf/3.21.9")
        self.requires("re2/20230201")
        self.requires("cxxopts/3.0.0", private=True)
        self.requires("date/3.0.1", private=True)
        self.requires("dlpack/0.4", private=True)
        self.requires("eigen/3.4.0", private=True)
        self.requires("flatbuffers/1.12.0", private=True)
        self.requires("fp16/cci.20210320", private=True)
        self.requires("fxdiv/cci.20200417", private=True)
        self.requires("ms-gsl/4.0.0", private=True)
        self.requires("nlohmann_json/3.11.2", private=True)
        self.requires("psimd/cci.20200517", private=True)
        self.requires("pthreadpool/cci.20210218", private=True)
        self.requires("pybind11/2.10.1", private=True)
        self.requires("safeint/3.24", private=True)
        self.requires("xnnpack/cci.20220801", private=True)
        # onnx requirement needs source
        # self.requires("onnx/1.11.0")

    def build_requirements(self):
        self.tool_requires("protobuf/3.21.9")
        self.test_requires("gtest/1.13.0")
        self.test_requires("benchmark/1.7.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_MESSAGE_LOG_LEVEL"] = "DEBUG"
        if self.options.shared:
            tc.variables["onnxruntime_BUILD_SHARED_LIB"] = True
        if not is_apple_os(self) and self.options.with_cuda:
            tc.variables["onnxruntime_USE_CUDA"] = True
        if self.settings.os == "Windows" and self.options.with_dml:
            tc.variables["onnxruntime_USE_DML"] = True
        if is_apple_os(self) and self.options.with_coreml:
            tc.variables["onnxruntime_USE_COREML"] = True
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "cmake"))
        cmake.build()

    def package(self):
        include = os.path.join(self.source_folder, "include", "onnxruntime")
        self.copy("*.h", src=os.path.join(include, "core", "session"), dst="include")
        self.copy("provider_options.h", src=os.path.join(include, "core", "framework"), dst="include")
        providers = ["cpu"]
        if is_apple_os(self) and self.options.with_coreml:
            providers.append("coreml")
        if self.settings.os == "Windows" and self.options.with_dml:
            providers.append("dml")
        if not is_apple_os(self) and self.options.with_cuda:
            providers.append("cuda")
        for provider in providers:
            self.copy("*.h", src=os.path.join(include, "core", "providers", provider), dst="include")
        lib_dir = self.build_folder
        exts = (".a", ".lib", ".dll", ".dylib", ".so")
        for root, dirs, files in os.walk(lib_dir):
            for name in files:
                if os.path.splitext(name)[1] in exts:
                    self.copy(name, src=root, dst="lib")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OnnxRuntime")
        self.cpp_info.set_property("cmake_target_name", "OnnxRuntime::OnnxRuntime")
        self.cpp_info.set_property("pkg_config_name", "onnxruntime")
        self.cpp_info.libs = [
            "onnxruntime_session",
            "onnxruntime_optimizer",
            "onnxruntime_providers",
            "onnxruntime_framework",
            "onnxruntime_graph",
            "onnxruntime_util",
            "onnxruntime_mlas",
            "onnxruntime_common",
            "onnxruntime_flatbuffers",
            "onnx",
            "onnx_proto",
        ]
        if is_apple_os(self):
            self.cpp_info.frameworks = ["Foundation"]
            if self.options.with_coreml:
                self.cpp_info.frameworks.append("CoreML")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
        if self.settings.os == "Windows" and self.options.with_dml:
            self.cpp_info.system_libs += ["DirectML"]
        if not is_apple_os(self) and self.options.with_cuda:
            self.cpp_info.system_libs += ["cublasLt", "cublas", "cudnn", "curand", "cufft"]

        self.cpp_info.names["cmake_find_package"] = "OnnxRuntime"
        self.cpp_info.names["cmake_find_package_multi"] = "OnnxRuntime"
