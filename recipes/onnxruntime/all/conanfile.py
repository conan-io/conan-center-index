from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
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
        "with_cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_xnnpack": False,
        "with_cuda": False,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        if is_apple_os(self) and Version(self.version) >= "1.17.0":
            return 20  # https://github.com/microsoft/onnxruntime/blob/8f5c79cb63f09ef1302e85081093a3fe4da1bc7d/cmake/CMakeLists.txt#L43-L47
        return 17

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "1.16.0":
            return {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "7",
                "clang": "5",
                "apple-clang": "10",
            }
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "9",
            "clang": "5",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # onnxruntime forces this to be True
        # https://github.com/microsoft/onnxruntime/blob/be76e1e1b8e2914e448d12a0cc683c00014c0490/cmake/external/onnxruntime_external_deps.cmake#L542
        self.options["onnx"].disable_static_registration = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        required_onnx_version = self.conan_data["onnx_version_map"][self.version]
        self.requires(f"onnx/{required_onnx_version}")
        self.requires("abseil/20240116.1")
        self.requires("protobuf/3.21.12")
        self.requires("date/3.0.1")
        self.requires("re2/20231101")
        if Version(self.version) >= "1.18":
            self.requires("flatbuffers/23.5.26")
        else:
            # v1.* is required, newer versions are not compatible
            self.requires("flatbuffers/1.12.0")
        # using 1.84.0+ fails on CCI as it prevents the cpp 17 version to be picked up when building with cpp 20
        self.requires("boost/1.83.0", headers=True, libs=False)  # for mp11, header only, no need for libraries
        self.requires("safeint/3.0.28")
        self.requires("nlohmann_json/3.11.3")
        self.requires("eigen/3.4.0")
        self.requires("ms-gsl/4.0.0")
        if Version(self.version) >= "1.17.0":
            self.requires("cpuinfo/cci.20231129")
        else:
            self.requires("cpuinfo/cci.20220618")  # Newer versions are not compatible
        if self.settings.os != "Windows":
            self.requires("nsync/1.26.0")
        else:
            self.requires("wil/1.0.240803.1")
        if self.options.with_xnnpack:
            if Version(self.version) >= "1.17.0":
                self.requires("xnnpack/cci.20230715")
            else:
                self.requires("xnnpack/cci.20220801")
        if self.options.with_cuda:
            self.requires("cutlass/3.5.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires minimum compiler version {minimum_version}."
            )
        if not self.dependencies["onnx"].options.disable_static_registration:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires onnx compiled with `-o onnx:disable_static_registration=True`."
            )

    def validate_build(self):
        if self.version >= Version("1.15.0") and self.options.shared and sys.version_info[:2] < (3, 8):
            # https://github.com/microsoft/onnxruntime/blob/638146b79ea52598ece514704d3f592c10fab2f1/cmake/CMakeLists.txt#LL500C12-L500C12
            raise ConanInvalidConfiguration(
                f"{self.ref} requires Python 3.8+ to be built as shared."
            )
        if self.settings.os == "Windows" and self.dependencies["abseil"].options.shared:
            raise ConanInvalidConfiguration("Using abseil shared on Windows leads to link errors.")

    def build_requirements(self):
        # Required by upstream https://github.com/microsoft/onnxruntime/blob/v1.16.1/cmake/CMakeLists.txt#L5
        self.tool_requires("cmake/[>=3.26 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # disable downloading dependencies to ensure conan ones are used
        tc.variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True
        if self.version >= Version("1.15.0") and self.options.shared:
            # Need to replace windows path separators with linux path separators to keep CMake from crashing
            tc.variables["Python_EXECUTABLE"] = sys.executable.replace("\\", "/")

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

        if Version(self.version) >= "1.17":
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

        vbe = VirtualBuildEnv(self)
        vbe.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "onnxruntime_external_deps.cmake",
             src=os.path.join(self.export_sources_folder, "cmake"),
             dst=os.path.join(self.source_folder, "cmake", "external"))
        # Avoid parsing of git commit info
        if Version(self.version) >= "15.0":
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "CMakeLists.txt"),
                            "if (Git_FOUND)", "if (FALSE)")
        if Version(self.version) >= "1.17":
            # https://github.com/microsoft/onnxruntime/commit/5bfca1dc576720627f3af8f65e25af408271079b
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "onnxruntime_providers_cuda.cmake"),
                            'option(onnxruntime_NVCC_THREADS "Number of threads that NVCC can use for compilation." 1)', 
                            'set(onnxruntime_NVCC_THREADS "1" CACHE STRING "Number of threads that NVCC can use for compilation.")')

    def build(self):
        self._patch_sources()
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
            if self.options.with_xnnpack:
                onnxruntime_libs.append("providers_xnnpack")
            self.cpp_info.libs = [f"onnxruntime_{lib}" for lib in onnxruntime_libs]

        if Version(self.version) < "1.16.0" or not self.options.shared:
            self.cpp_info.includedirs.append("include/onnxruntime/core/session")
        else:
            self.cpp_info.includedirs.append("include/onnxruntime")

        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")
        if self.settings.os in ["Linux", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("pthread")
        if is_apple_os(self):
            self.cpp_info.frameworks.append("Foundation")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("shlwapi")

        # conanv1 doesn't support traits and we only need headers from boost
        self.cpp_info.requires = [
            "abseil::abseil",
            "protobuf::protobuf",
            "date::date",
            "re2::re2",
            "onnx::onnx",
            "flatbuffers::flatbuffers",
            "boost::headers",
            "safeint::safeint",
            "nlohmann_json::nlohmann_json",
            "eigen::eigen",
            "ms-gsl::ms-gsl",
            "cpuinfo::cpuinfo"
        ]
        if self.settings.os != "Windows":
            self.cpp_info.requires.append("nsync::nsync")
        else:
            self.cpp_info.requires.append("wil::wil")
        if self.options.with_xnnpack:
            self.cpp_info.requires.append("xnnpack::xnnpack")
        if self.options.with_cuda:
            self.cpp_info.requires.append("cutlass::cutlass")

        # https://github.com/microsoft/onnxruntime/blob/v1.16.0/cmake/CMakeLists.txt#L1759-L1763
        self.cpp_info.set_property("cmake_file_name", "onnxruntime")
        self.cpp_info.set_property("cmake_target_name", "onnxruntime::onnxruntime")
        # https://github.com/microsoft/onnxruntime/blob/v1.14.1/cmake/CMakeLists.txt#L1584
        self.cpp_info.set_property("pkg_config_name", "onnxruntime")
