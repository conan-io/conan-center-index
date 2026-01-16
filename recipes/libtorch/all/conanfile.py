import os
import sys
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import (
    apply_conandata_patches,
    export_conandata_patches,
    get,
    rmdir, copy,
)
from conan.tools.apple import is_apple_os
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from pathlib import Path
from conan.tools.system import PipEnv

required_conan_version = ">=2.23"

class LibtorchRecipe(ConanFile):
    name = "libtorch"
    package_type = "library"
    description = "Torch library for C++"
    topics = ("machine-learning", "deep-learning", "neural-network", "pytorch")
    license = "BSD-3-Clause"
    homepage = "https://github.com/pytorch/pytorch"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gflags": [True, False],
        "with_kleidiai": [True, False],
        "with_mimalloc": [True, False],
        "with_nnpack": [True, False],
        "with_numa": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gflags": False,
        "with_kleidiai": True,
        "with_mimalloc": False,
        "with_nnpack": True,
        "with_numa": True,
    }

    implements = ["auto_shared_fpic"]

    @property
    def _is_clang_cl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows" and \
               self.settings.compiler.get_safe("runtime")

    @property
    def _has_backtrace(self):
        # Even though backtrace is Windows compatible, libtorch expects to find it only on Unix-like systems
        # Failing otherwise as it will include headers not present in windows
        return self.settings.os != "Windows"

    @property
    def _has_ittapi(self):
        return self.settings.arch in ("x86", "x86_64")

    @property
    def _has_qnnpack(self):
        return not is_msvc(self) and not self._is_clang_cl

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Mimalloc is true by default in libtorch
            self.options.with_mimalloc = True
            del self.options.with_nnpack
        if self.settings.os != "Linux":
            # Only supported on Linux
            del self.options.with_numa
        if "arm" not in self.settings.arch:
            del self.options.with_kleidiai

    def requirements(self):
        self.requires("concurrentqueue/1.0.4", transitive_headers=True)
        self.requires("cpp-httplib/[~0.30]")
        self.requires("cpuinfo/[>=cci.20250321]", transitive_headers=True)
        self.requires("eigen/[>=3 <4]")
        # mobile_bytecode_generated.h is fixed to 24.12.23. If we want to support other versions, we will need to regenerate the header
        self.requires("flatbuffers/24.12.23", transitive_headers=True)
        self.requires("fmt/[^10]", transitive_libs=True, transitive_headers=True)
        self.requires("fp16/cci.20210320")
        self.requires("fxdiv/cci.20200417")
        self.requires("libuv/[>=1 <2]")
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        self.requires("onnx/[>=1.20 <2]", transitive_libs=True, transitive_headers=True)
        self.requires("openblas/[^0.3.27]", transitive_libs=True)
        self.requires("opentelemetry-cpp/1.24.0")
        self.requires("pocketfft/0.0.0.cci.20240801")
        self.requires("protobuf/[>=4.25.3 <7]")
        self.requires("psimd/cci.20200517")
        self.requires("pthreadpool/cci.20231129", transitive_headers=True)
        self.requires("sleef/[>=3.9]", transitive_libs=True, transitive_headers=True)
        self.requires("xnnpack/[>=cci.20241203]", transitive_libs=True, transitive_headers=True)
        # miniz will be kept vendored as it has been slightly modified by libtorch, for example, they have added
        # MINIZ_DISABLE_ZIP_READER_CRC32_CHECKS to disable crc32 checks when reading zip files.

        if self._has_backtrace:
            self.requires("libbacktrace/cci.20210118")
        if self._has_ittapi:
            self.requires("ittapi/3.25.5")
        if self.options.with_gflags:
            self.requires("gflags/2.2.2", transitive_headers=True)
        if self.options.get_safe("with_kleidiai"):
            self.requires("kleidiai/1.18.0")
        if self.options.with_mimalloc:
            self.requires("mimalloc/[>=2.2.4 <3]")
        if self.options.get_safe("with_nnpack"):
            self.requires("nnpack/0.0.0.cci.20230202")
        if self.options.get_safe("with_numa"):
            self.requires("libnuma/2.0.19")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27]")
        self.tool_requires("protobuf/<host_version>")

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        # Remove unneeded third_party folders
        third_party_allowed = ["miniz-3.0.2", "kineto"]
        for folder in Path(self.source_folder).joinpath("third_party").iterdir():
            if folder.is_dir() and folder.name not in third_party_allowed:
                rmdir(self, folder)

    def generate(self):
        # torchgen/gen.py includes pyyaml and typing_extensions modules

        deps = CMakeDeps(self)
        deps.set_property("concurrentqueue", "cmake_target_name", "moodycamel")
        deps.set_property("cpp-httplib", "cmake_target_name", "httplib")
        deps.set_property("cpuinfo", "cmake_target_name", "cpuinfo")
        deps.set_property("eigen", "cmake_file_name", "EIGEN3")
        # Force flatbuffers::flatbuffers target even when flatbuffers dynamically linked
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        # This might be non header only, but upstream expects this target
        deps.set_property("fmt", "cmake_target_name", "fmt::fmt-header-only")
        deps.set_property("fp16", "cmake_target_name", "fp16")
        deps.set_property("fxdiv", "cmake_target_name", "fxdiv")
        deps.set_property("gflags", "cmake_target_name", "gflags")
        deps.set_property("ittapi", "cmake_file_name", "ITT")
        deps.set_property("libbacktrace", "cmake_file_name", "Backtrace")
        deps.set_property("libnuma", "cmake_additional_variables_prefixes", ["Numa"])
        deps.set_property("libnuma", "cmake_file_name", "NUMA")
        # Vendorized version only uses static so the target name is hardcoded, but this also works with shared
        deps.set_property("mimalloc", "cmake_target_name", "mimalloc-static")
        deps.set_property("nlohmann_json", "cmake_target_name", "nlohmann")
        deps.set_property("nnpack", "cmake_file_name", "NNPACK")
        deps.set_property("opentelemetry-cpp", "cmake_file_name", "OpenTelemetryApi")
        deps.set_property("psimd", "cmake_target_name", "psimd")
        deps.set_property("pthreadpool", "cmake_target_name", "pthreadpool")
        deps.set_property("sleef", "cmake_target_name", "sleef")
        deps.set_property("xnnpack", "cmake_target_name", "XNNPACK")
        deps.generate()

        tc = CMakeToolchain(self)

        tc.cache_variables["USE_LITE_PROTO"] = self.dependencies.host["protobuf"].options.lite

        tc.cache_variables["CMAKE_BUILD_TYPE"] = str(self.settings.build_type)
        tc.cache_variables["BUILD_TEST"] = "OFF"
        tc.cache_variables["USE_SYSTEM_LIBS"] = True
        tc.cache_variables["BUILD_PYTHON"] = "OFF"
        tc.cache_variables["BLAS"] = "OpenBLAS"

        # FIXME: Upstream sets this to empty only on macos when building thru bazel.
        tc.preprocessor_definitions["CLOG_VISIBILITY"] = ""
        tc.cache_variables["CAFFE2_LINK_LOCAL_PROTOBUF"] = False
        tc.cache_variables["BUILD_CUSTOM_PROTOBUF"] = False
        tc.cache_variables["CAFFE2_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)

        # Disable parallelism
        tc.cache_variables["USE_OPENMP"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_OpenMP"] = True
        tc.cache_variables["USE_MKLDNN"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_MKL"] = True

        tc.cache_variables["USE_DISTRIBUTED"] = False
        tc.cache_variables["USE_CCACHE"] = False
        tc.cache_variables["USE_CUDA"] = False
        tc.cache_variables["USE_FBGEMM"] = False  # TODO unvendor after adding to CCI
        tc.cache_variables["USE_GLOO"] = False    # TODO unvendor after adding to CCI
        tc.cache_variables["USE_KINETO"] = False  # TODO unvendor after adding to CCI
        tc.cache_variables["USE_MAGMA"] = False   # TODO unvendor after adding to CCI
        tc.cache_variables["USE_MPI"] = False
        tc.cache_variables["USE_NUMPY"] = False
        tc.cache_variables["USE_TENSORPIPE"] = self.settings.os == "Windows"

        if not self._has_backtrace:
            tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Backtrace"] = True
        tc.cache_variables["USE_PYTORCH_QNNPACK"] = self._has_qnnpack
        tc.cache_variables["USE_GFLAGS"] = self.options.with_gflags
        tc.cache_variables["USE_KLEIDIAI"] = self.options.get_safe("with_kleidiai")
        tc.cache_variables["USE_MIMALLOC"] = self.options.with_mimalloc
        tc.cache_variables["USE_NNPACK"] = self.options.get_safe("with_nnpack")
        tc.cache_variables["USE_NUMA"] = self.options.get_safe("with_numa")

        tc.cache_variables['Python_FIND_UNVERSIONED_NAMES'] = 'FIRST'
        tc.cache_variables['Python_FIND_STRATEGY'] = 'LOCATION'
        tc.cache_variables["Python_ROOT_DIR"] = os.path.join(self.build_folder, "conan_pipenv").replace("\\", "/")
        tc.cache_variables["Python_EXECUTABLE"] = os.path.join(self.build_folder, "conan_pipenv", "bin" if sys.platform != "win32" else "Scripts", "python" + (".exe" if sys.platform == "win32" else "")).replace("\\", "/")

        tc.generate()

        pip = PipEnv(self)
        pip.install(["pyyaml", "typing-extensions"])
        pip.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Vendorized dependencies, remove once added to CCI
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "third_party", "kineto"), dst=os.path.join(self.package_folder, "licenses", "kineto"))
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "third_party", "miniz-3.0.2"), dst=os.path.join(self.package_folder, "licenses", "miniz"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share", "cmake"))

    def package_info(self):
        def _whole_archive(component, lib_name):
            component.libs = [lib_name]
            libname = lib_name if self.settings.os == "Windows" else 'lib' + lib_name
            lib_path = os.path.join(self.package_folder, component.libdir, libname)
            if self.options.shared:
                return component
            flags = ""
            if is_apple_os(self):
                flags = f"-Wl,-force_load,{lib_path + '.a'}"
            elif self.settings.compiler == "msvc":
                flags = f"-WHOLEARCHIVE:{lib_path}"
            elif self.settings.os == "Linux":
                flags = f"-Wl,--whole-archive,{lib_path}.a,--no-whole-archive"
            component.exelinkflags.append(flags)
            component.sharedlinkflags.append(flags)
            return component

        self.cpp_info.set_property("cmake_file_name", "Torch")
        # Make it compatible with upstream example usages
        self.cpp_info.set_property("cmake_additional_variables_prefixes", ["TORCH"])

        # C10 component
        c10 = _whole_archive(self.cpp_info.components["c10"], "c10")
        c10.requires = [
            "eigen::eigen",
            "fmt::fmt",
            "concurrentqueue::concurrentqueue",
            "cpuinfo::cpuinfo",
        ]
        if is_apple_os(self):
            for framework in [
                "Foundation",
                "IOKit",
                "Metal",
                "MetalPerformanceShaders",
                "MetalPerformanceShadersGraph",
            ]:
                c10.sharedlinkflags.append(f"-Wl,-weak_framework,{framework}")
                c10.exelinkflags.append(f"-Wl,-weak_framework,{framework}")
        if self._has_backtrace:
            c10.requires.append("libbacktrace::libbacktrace")
        if self.options.with_mimalloc:
            c10.requires.append("mimalloc::mimalloc")
        if self.options.with_gflags:
            c10.requires.append("gflags::gflags")

        # QNNPACK vendored library component
        if self._has_qnnpack:
            # TODO: is linking with 'log' in Android, check
            self.cpp_info.components["clog"].libs = ["clog"]

            self.cpp_info.components["pytorch_qnnpack"].libs = ["pytorch_qnnpack"]
            self.cpp_info.components["pytorch_qnnpack"].requires = [
                "clog",
                "cpuinfo::cpuinfo",
                "fp16::fp16",
                "fxdiv::fxdiv",
                "psimd::psimd",
                "pthreadpool::pthreadpool",
            ]

        # Torch CPU component
        torch_cpu = _whole_archive(self.cpp_info.components["torch_cpu"], "torch_cpu")
        torch_cpu.bindirs = ["lib"]  # for torch_cpu.dll on Windows
        torch_cpu.requires = [
            "c10",
            "cpp-httplib::cpp-httplib",
            "flatbuffers::flatbuffers",
            "fp16::fp16",
            "fxdiv::fxdiv",
            "libuv::libuv",
            "nlohmann_json::nlohmann_json",
            "onnx::libonnx",
            "openblas::openblas",
            "opentelemetry-cpp::opentelemetry-cpp",
            "pocketfft::pocketfft",
            "protobuf::libprotobuf",
            "psimd::psimd",
            "pthreadpool::pthreadpool",
            "sleef::sleef",
            "xnnpack::xnnpack",
        ]
        if self._has_qnnpack:
            torch_cpu.requires.append("pytorch_qnnpack")
        if self._has_ittapi:
            torch_cpu.requires.append("ittapi::ittapi")
        if self.settings.os != "Windows":
            torch_cpu.defines = ["USE_RPC"]
        if self.options.with_gflags:
            torch_cpu.requires.append("gflags::gflags")
        if self.options.get_safe("with_kleidiai"):
            torch_cpu.requires.append("kleidiai::kleidiai")
        if self.options.get_safe("with_nnpack"):
            torch_cpu.requires.append("nnpack::nnpack")
        if self.options.get_safe("with_numa"):
            torch_cpu.requires.append("libnuma::libnuma")

        # Torch global component
        self.cpp_info.components["torch"].libs = ["torch"]
        self.cpp_info.components["torch"].requires = ["torch_cpu"]
        self.cpp_info.components["torch"].includedirs = ["include/torch/csrc/api/include", "include"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "rt", "m", "pthread"])

        # torch_global_deps library only generated in shared builds should not be modelled by conan as this library
        # is aimed to be dlopen in runtime
