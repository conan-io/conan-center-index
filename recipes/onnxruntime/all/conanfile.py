import os
import sys

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file

required_conan_version = ">=2"


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
        "with_cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_xnnpack": False,
        "with_cuda": False,
    }
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        required_onnx_version = self.conan_data["onnx_version_map"][self.version]
        self.requires(f"onnx/{required_onnx_version}")
        self.requires("abseil/[>=20240116.1 <=20250814.0]")
        self.requires("protobuf/[>=3.21.12 <7]")
        self.requires("date/[>=3.0.1 <3.1]")
        self.requires("re2/[>=20231101]")
        self.requires("flatbuffers/23.5.26")
        self.requires("boost/[>=1.83.0 <1.90.0]", headers=True, libs=False)  # for mp11, header only, no need for libraries
        self.requires("safeint/3.0.28")
        self.requires("nlohmann_json/[>=3.11.3 <3.12]")
        self.requires("eigen/[>=5.0.1 <6]")
        self.requires("ms-gsl/4.0.0")
        if self.settings.os != "Windows":
            self.requires("nsync/1.26.0")
        else:
            self.requires("wil/1.0.240803.1")
        if self.options.with_xnnpack:
            self.requires("xnnpack/[>=cci.20241203]")
            self.requires("pthreadpool/cci.20231129")
        if self.options.with_cuda:
            self.requires("cutlass/3.5.0")
        self.requires("cpuinfo/[>=cci.20250110]")

    def validate(self):
        check_min_cppstd(self, 17)
        onnx = self.dependencies["onnx"]
        if not onnx.options.disable_static_registration:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires onnx compiled with `-o onnx:disable_static_registration=True`."
            )
        if onnx.options.get_safe("shared"):
            # Commented here: https://github.com/onnx/onnx/pull/7505#issuecomment-3601468150
            raise ConanInvalidConfiguration("There are link errors using 'onnx/*:shared=True',"
                                            " use '-o onnx/*:shared=False' instead.")

    def validate_build(self):
        if self.settings.os == "Windows" and self.dependencies["abseil"].options.shared:
            raise ConanInvalidConfiguration("Using abseil shared on Windows leads to link errors.")

    def build_requirements(self):
        # Required by upstream https://github.com/microsoft/onnxruntime/blob/v1.16.1/cmake/CMakeLists.txt#L5
        self.tool_requires("cmake/[>=3.28]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        # disable downloading dependencies to ensure conan ones are used
        tc.variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True

        tc.variables["onnxruntime_BUILD_SHARED_LIB"] = self.options.shared
        tc.variables["onnxruntime_USE_FULL_PROTOBUF"] = not self.dependencies["protobuf"].options.lite
        tc.variables["onnxruntime_USE_XNNPACK"] = self.options.with_xnnpack

        tc.variables["onnxruntime_USE_CUDA"] = self.options.with_cuda
        tc.variables["onnxruntime_BUILD_UNIT_TESTS"] = False
        tc.variables["onnxruntime_DISABLE_CONTRIB_OPS"] = False
        tc.variables["onnxruntime_USE_FLASH_ATTENTION"] = False
        tc.variables["onnxruntime_DISABLE_RTTI"] = False
        tc.variables["onnxruntime_DISABLE_EXCEPTIONS"] = False

        tc.variables["onnxruntime_ARMNN_RELU_USE_CPU"] = False
        tc.variables["onnxruntime_ARMNN_BN_USE_CPU"] = False
        tc.variables["onnxruntime_ENABLE_CPU_FP16_OPS"] = False
        tc.variables["onnxruntime_ENABLE_EAGER_MODE"] = False
        tc.variables["onnxruntime_ENABLE_LAZY_TENSOR"] = False

        tc.variables["onnxruntime_ENABLE_CUDA_EP_INTERNAL_TESTS"] = False
        tc.variables["onnxruntime_USE_NEURAL_SPEED"] = False
        tc.variables["onnxruntime_USE_MEMORY_EFFICIENT_ATTENTION"] = False

        # Disable a warning that gets converted to an error
        tc.preprocessor_definitions["_SILENCE_ALL_CXX23_DEPRECATION_WARNINGS"] = "1"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("boost::headers", "cmake_target_name", "Boost::mp11")
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "onnxruntime_external_deps.cmake",
             src=os.path.join(self.export_sources_folder, "cmake"),
             dst=os.path.join(self.source_folder, "cmake", "external"))
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "CMakeLists.txt"),
                        "if (Git_FOUND)", "if (FALSE)")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cmake", cli_args=["--compile-no-warning-as-error"])
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["onnxruntime"]
        else:
            # order is important
            # https://github.com/microsoft/onnxruntime/blob/v1.23.2/cmake/onnxruntime.cmake#L240
            onnxruntime_libs = [
                "session",
                *(["providers_xnnpack"] if self.options.with_xnnpack else []),
                "optimizer",
                "providers",
                "lora",
                "framework",
                "graph",
                "util",
                "mlas",
                "common",
                "flatbuffers",
            ]
            self.cpp_info.libs = [f"onnxruntime_{lib}" for lib in onnxruntime_libs]

        self.cpp_info.includedirs.append("include/onnxruntime")
        if not self.options.shared:
            self.cpp_info.includedirs.append("include/onnxruntime/core/session")

        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")
        if self.settings.os in ["Linux", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("pthread")
        if is_apple_os(self):
            self.cpp_info.frameworks.append("Foundation")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("shlwapi")

        # https://github.com/microsoft/onnxruntime/blob/v1.16.0/cmake/CMakeLists.txt#L1759-L1763
        self.cpp_info.set_property("cmake_file_name", "onnxruntime")
        self.cpp_info.set_property("cmake_target_name", "onnxruntime::onnxruntime")
        # https://github.com/microsoft/onnxruntime/blob/v1.14.1/cmake/CMakeLists.txt#L1584
        self.cpp_info.set_property("pkg_config_name", "onnxruntime")
