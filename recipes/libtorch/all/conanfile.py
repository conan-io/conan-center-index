import os
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.6"


class LibtorchConan(ConanFile):
    name = "libtorch"
    description = "Tensors and Dynamic neural networks with strong GPU acceleration."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pytorch.org"
    topics = ("machine-learning", "deep-learning", "neural-network", "gpu", "tensor")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "blas": ["eigen", "openblas", "veclib"],
        "build_lazy_ts_backend": [True, False],
        "build_lite_interpreter": [True, False],
        "coreml_delegate": [True, False],
        "fakelowp": [True, False],
        "observers": [True, False],
        "utilities": [True, False],
        "vulkan_fp16_inference": [True, False],
        "vulkan_relaxed_precision": [True, False],
        "with_fbgemm": [True, False],
        "with_gflags": [True, False],
        "with_glog": [True, False],
        "with_itt": [True, False],
        "with_kineto": [True, False],
        "with_mimalloc": [True, False],
        "with_nnpack": [True, False],
        "with_numa": [True, False],
        "with_opencl": [True, False],
        "with_openmp": [True, False],
        "with_qnnpack": [True, False],
        "with_vulkan": [True, False],
        "with_xnnpack": [True, False],
        # TODO
        # "build_lazy_cuda_linalg": [True, False],
        # "debug_cuda": [True, False],
        # "with_cuda": [True, False],
        # "with_cudnn": [True, False],
        # "with_cusparselt": [True, False],
        # "with_magma": [True, False],
        # "with_metal": [True, False],
        # "with_mkldnn": [True, False],
        # "with_mps": [True, False],
        # "with_nccl": [True, False],
        # "with_nnapi": [True, False],
        # "with_nvrtc": [True, False],
        # "with_rocm": [True, False],
        # "with_snpe": [True, False],
        # "with_xpu": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "blas": "openblas",
        "build_lazy_ts_backend": True,
        "build_lite_interpreter": False,
        "coreml_delegate": False,
        "fakelowp": False,
        "observers": False,
        "utilities": False,
        "vulkan_fp16_inference": False,
        "vulkan_relaxed_precision": False,
        "with_fbgemm": True,
        "with_gflags": False,
        "with_glog": False,
        "with_itt": True,
        "with_kineto": True,
        "with_mimalloc": False,
        "with_nnpack": True,
        "with_numa": True,
        "with_opencl": False,
        "with_openmp": True,
        "with_qnnpack": True,
        "with_vulkan": True,
        "with_xnnpack": True,
        # TODO
        # "build_lazy_cuda_linalg": False,
        # "debug_cuda": False,
        # "with_cuda": False,
        # "with_cudnn": True,
        # "with_cusparselt": True,
        # "with_mkldnn": False,
        # "with_magma": True,
        # "with_metal": False,
        # "with_mps": True,
        # "with_nccl": True,
        # "with_nnapi": False,
        # "with_nvrtc": False,
        # "with_rocm": False,
        # "with_snpe": False,
        # "with_xpu": False,
    }
    options_description = {
        "blas": "Which BLAS backend to use",
        "build_lazy_cuda_linalg": "Build cuda linalg ops as separate library",
        "build_lazy_ts_backend": "Build the lazy Torchscript backend, not compatible with mobile builds",
        "build_lite_interpreter": "Build Lite Interpreter",
        "coreml_delegate": "Use the CoreML backend through delegate APIs",
        "debug_cuda": "When compiling DEBUG, also attempt to compile CUDA with debug flags (may cause nvcc to OOM)",
        "fakelowp": "Use FakeLowp operators instead of FBGEMM",
        "observers": "Use observers module",
        "utilities": "Build utility executables",
        "vulkan_fp16_inference": "Vulkan - Use fp16 inference",
        "vulkan_relaxed_precision": "Vulkan - Use relaxed precision math in the kernels (mediump)",
        "with_cuda": "Use CUDA",
        "with_cudnn": "Use cuDNN",
        "with_cusparselt": "Use cuSPARSELt",
        "with_fbgemm": "Use FBGEMM (quantized 8-bit server operators)",
        "with_gflags": "Use GFLAGS",
        "with_glog": "Use GLOG",
        "with_itt": "Use Intel VTune Profiler ITT functionality",
        "with_kineto": "Use Kineto profiling library",
        "with_magma": "Use MAGMA linear algebra library",
        "with_metal": "Use Metal for iOS build",
        "with_mimalloc": "Use mimalloc",
        "with_mkldnn": "Use MKLDNN. Only available on x86, x86_64, and AArch64.",
        "with_mps": "Use MPS for macOS build",
        "with_nccl": "Use NCCL and RCCL",
        "with_nnapi": "Use NNAPI for Android build",
        "with_nnpack": "Use NNPACK CPU acceleration library",
        "with_numa": "Use NUMA. Only available on Linux.",
        "with_nvrtc": "Use NVRTC",
        "with_opencl": "Use OpenCL",
        "with_openmp": "Use OpenMP for parallel code",
        "with_qnnpack": "Use ATen/QNNPACK (quantized 8-bit operators)",
        "with_rocm": "Use ROCm (HIP)",
        "with_snpe": "Use Qualcomm's SNPE library",
        "with_vulkan": "Use Vulkan GPU backend",
        "with_xnnpack": "Use XNNPACK",
        "with_xpu": "Use XPU (SYCL) backend for Intel GPUs",
    }
    no_copy_source = True
    provides = ["miniz", "pocketfft", "kineto", "nnpack", "qnnpack"]

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "9",
            "msvc": "191",
            "Visual Studio": "15",
        }

    @property
    def _is_mobile_os(self):
        return self.settings.os in ["Android", "iOS"]

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_qnnpack
        if not is_apple_os(self):
            self.options.rm_safe("with_metal")
            self.options.rm_safe("with_magma")
            self.options.rm_safe("with_mps")
        if self.settings.os != "Linux":
            del self.options.with_numa
        if self.settings.os != "Android":
            self.options.rm_safe("with_nnapi")
            self.options.rm_safe("with_snpe")
            self.options.with_vulkan = False
        if self._is_mobile_os:
            self.options.blas = "eigen"
            self.options.build_lazy_ts_backend = False
            del self.options.with_fbgemm
            # del self.options.distributed
        if self.settings.arch not in ["x86", "x86_64", "armv8"]:
            self.options.rm_safe("with_mkldnn")
        if not is_apple_os(self) or self.settings.os not in ["Linux", "Android"]:
            del self.options.with_nnpack
        self.options.with_itt = self.settings.arch in ["x86", "x86_64"]

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.get_safe("with_cuda"):
            self.options.rm_safe("build_lazy_cuda_linalg")
            self.options.rm_safe("debug_cuda")
            self.options.rm_safe("with_cudnn")
            self.options.rm_safe("with_cusparselt")
            self.options.rm_safe("with_nvrtc")
            if not self.options.get_safe("with_rocm"):
                self.options.rm_safe("with_nccl")
        if not self.options.with_vulkan:
            self.options.rm_safe("vulkan_fp16_inference")
            self.options.rm_safe("vulkan_relaxed_precision")
        if not self.options.get_safe("fbgemm"):
            self.options.rm_safe("fakelowp")

        # numa static can't be linked into shared libs.
        # Because Caffe2_detectron_ops* libs are always shared, we have to force
        # libnuma shared even if libtorch:shared=False
        if self.options.get_safe("with_numa"):
            self.options["libnuma"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _depends_on_sleef(self):
        return not self._is_mobile_os and not self.settings.os == "Emscripten"

    @property
    def _depends_on_pthreadpool(self):
        return self._is_mobile_os or self._use_nnpack_family

    @property
    def _depends_on_flatbuffers(self):
        return not self._is_mobile_os

    @property
    def _blas_cmake_option_value(self):
        return {
            "eigen": "Eigen",
            "atlas": "ATLAS",
            "openblas": "OpenBLAS",
            "mkl": "MKL",
            "veclib": "vecLib",
            "flame": "FLAME",
            "generic": "Generic"
        }[str(self.options.blas)]

    @property
    def _use_nnpack_family(self):
        return any(self.options.get_safe(f"with_{name}") for name in ["nnpack", "qnnpack", "xnnpack"])

    def requirements(self):
        self.requires("cpuinfo/cci.20231129")
        self.requires("eigen/3.4.0")
        # fmt/11.x is not yet supported as of v2.4.0
        self.requires("fmt/10.2.1", transitive_headers=True, transitive_libs=True)
        self.requires("foxi/cci.20210217", libs=False)
        self.requires("onnx/1.16.1", transitive_headers=True, transitive_libs=True)
        self.requires("protobuf/3.21.12")
        self.requires("fp16/cci.20210320")
        self.requires("cpp-httplib/0.16.0")
        self.requires("libbacktrace/cci.20210118")
        if self._depends_on_sleef:
            self.requires("sleef/3.6")
        if self._depends_on_flatbuffers:
            self.requires("flatbuffers/24.3.25", libs=False)
        if self.options.blas == "openblas":
            # Also provides LAPACK, currently
            self.requires("openblas/0.3.27")
        if self.options.with_openmp:
            self.requires("openmp/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_fbgemm:
            self.requires("fbgemm/0.8.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_glog:
            self.requires("glog/0.7.1", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_qnnpack"):
            self.requires("fxdiv/cci.20200417")
            self.requires("psimd/cci.20200517")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20240229")
        if self.options.with_itt:
            self.requires("ittapi/3.24.4")
        if self._depends_on_pthreadpool:
            self.requires("pthreadpool/cci.20231129")
        if self.options.get_safe("with_numa"):
            self.requires("libnuma/2.0.16")
        if self.options.with_opencl:
            self.requires("opencl-headers/2023.12.14")
            self.requires("opencl-icd-loader/2023.12.14")
        if self.options.with_vulkan:
            self.requires("vulkan-headers/1.3.268.0")
            self.requires("vulkan-loader/1.3.268.0")
        if self.options.with_mimalloc:
            self.requires("mimalloc/2.1.7")

        # miniz cannot be unvendored due to being slightly modified

        # TODO: unvendor
        # - pocketfft
        # - kineto
        # - nnpack
        # - qnnpack
        # TODO: add a recipe for
        # - magma
        # TODO: "distributed" option with sub-options for the following packages:
        # - openmpi
        # - ucc
        # - gloo
        # - tensorpipe

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.get_safe("with_numa") and not self.dependencies["libnuma"].options.shared:
            raise ConanInvalidConfiguration(
                "libtorch requires libnuma shared. Set '-o libnuma/*:shared=True', or disable numa with "
                "' -o libtorch/*:with_numa=False'"
            )

        if self.options.blas != "openblas":
            # FIXME: add an independent LAPACK package to CCI
            raise ConanInvalidConfiguration("'-o libtorch/*:blas=openblas' is currently required for LAPACK support")

        if self.options.blas == "veclib" and not is_apple_os(self):
            raise ConanInvalidConfiguration("veclib only available on Apple family OS")

        if self.options.get_safe("with_cuda"):
            self.output.warning("cuda recipe is not available, assuming that NVIDIA CUDA SDK is installed on your system")
            if self.options.get_safe("with_cudnn"):
                self.output.warning("cudnn recipe is not available, assuming that NVIDIA CuDNN is installed on your system")
            if self.options.get_safe("with_nvrtc"):
                self.output.warning("nvrtc recipe is not available, assuming that NVIDIA NVRTC is installed on your system")
            if self.options.get_safe("with_cusparselt"):
                self.output.warning("cusparselt recipe is not available, assuming that NVIDIA cuSPARSELt is installed on your system")
        if self.options.get_safe("with_nccl"):
            self.output.warning("nccl recipe is not available, assuming that NVIDIA NCCL is installed on your system")
        if self.options.get_safe("with_rocm"):
            self.output.warning("rocm recipe is not available, assuming that ROCm is installed on your system")
        if self.options.get_safe("with_xpu"):
            self.output.warning("xpu recipe is not available, assuming that Intel oneAPI is installed on your system")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")
        self.tool_requires("cpython/[~3.12]")
        if self._depends_on_flatbuffers:
            self.tool_requires("flatbuffers/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        # Keep only a restricted set of vendored dependencies.
        # Do it before build() to limit the amount of files to copy.
        allowed = ["pocketfft", "kineto", "miniz-2.1.0"]
        for path in Path(self.source_folder, "third_party").iterdir():
            if path.is_dir() and path.name not in allowed:
                rmdir(self, path)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_Torch_INCLUDE"] = "conan_deps.cmake"
        tc.variables["USE_SYSTEM_LIBS"] = True
        tc.variables["BUILD_TEST"] = False
        tc.variables["ATEN_NO_TEST"] = True
        tc.variables["BUILD_BINARY"] = self.options.utilities
        tc.variables["BUILD_CUSTOM_PROTOBUF"] = False
        tc.variables["BUILD_PYTHON"] = False
        tc.variables["BUILD_LITE_INTERPRETER"] = self.options.build_lite_interpreter
        tc.variables["CAFFE2_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.variables["USE_CUDA"] = self.options.get_safe("with_cuda", False)
        tc.variables["USE_XPU"] = self.options.get_safe("with_xpu", False)
        tc.variables["BUILD_LAZY_CUDA_LINALG"] = self.options.get_safe("build_lazy_cuda_linalg", False)
        tc.variables["USE_ROCM"] = self.options.get_safe("with_rocm", False)
        tc.variables["CAFFE2_STATIC_LINK_CUDA"] = False
        tc.variables["USE_CUDNN"] = self.options.get_safe("with_cudnn", False)
        tc.variables["USE_STATIC_CUDNN"] = False
        tc.variables["USE_CUSPARSELT"] = self.options.get_safe("with_cusparselt", False)
        tc.variables["USE_FBGEMM"] = self.options.with_fbgemm
        tc.variables["USE_KINETO"] = self.options.with_kineto
        tc.variables["USE_CUPTI_SO"] = True
        tc.variables["USE_FAKELOWP"] = self.options.get_safe("fakelowp", False)
        tc.variables["USE_GFLAGS"] = self.options.with_gflags
        tc.variables["USE_GLOG"] = self.options.with_glog
        tc.variables["USE_LITE_PROTO"] = self.dependencies["protobuf"].options.lite
        tc.variables["USE_MAGMA"] = self.options.get_safe("with_magma", False)
        tc.variables["USE_PYTORCH_METAL"] = self.options.get_safe("with_metal", False)
        tc.variables["USE_PYTORCH_METAL_EXPORT"] = self.options.get_safe("with_metal", False)
        tc.variables["USE_NATIVE_ARCH"] = False
        tc.variables["USE_MPS"] = self.options.get_safe("with_mps", False)
        tc.variables["USE_NCCL"] = self.options.get_safe("with_nccl", False)
        tc.variables["USE_RCCL"] = self.options.get_safe("with_nccl", False) and self.options.get_safe("with_rocm", False)
        tc.variables["USE_STATIC_NCCL"] = False
        tc.variables["USE_SYSTEM_NCCL"] = True
        tc.variables["USE_NNAPI"] = self.options.get_safe("with_nnapi", False)
        tc.variables["USE_NNPACK"] = self.options.get_safe("with_nnpack", False)
        tc.variables["USE_NUMA"] = self.options.get_safe("with_numa", False)
        tc.variables["USE_NVRTC"] = self.options.get_safe("with_nvrtc", False)
        tc.variables["USE_NUMPY"] = False
        tc.variables["USE_OBSERVERS"] = self.options.observers
        tc.variables["USE_OPENCL"] = self.options.with_opencl
        tc.variables["USE_OPENMP"] = self.options.with_openmp
        tc.variables["USE_PROF"] = False  # requires htrace
        tc.variables["USE_PYTORCH_QNNPACK"] = self.options.get_safe("with_qnnpack", False)
        tc.variables["USE_SNPE"] = self.options.get_safe("with_snpe", False)
        tc.variables["USE_SYSTEM_EIGEN_INSTALL"] = True
        tc.variables["USE_VALGRIND"] = False
        tc.variables["USE_VULKAN"] = self.options.with_vulkan
        tc.variables["USE_VULKAN_FP16_INFERENCE"] = self.options.get_safe("vulkan_fp16_inference", False)
        tc.variables["USE_VULKAN_RELAXED_PRECISION"] = self.options.get_safe("vulkan_relaxed_precision", False)
        tc.variables["USE_XNNPACK"] = self.options.with_xnnpack
        tc.variables["USE_ITT"] = self.options.with_itt
        tc.variables["USE_MKLDNN"] = self.options.get_safe("with_mkldnn", False)
        tc.variables["USE_MKLDNN_CBLAS"] = False  # This option is useless for libtorch
        tc.variables["USE_DISTRIBUTED"] = False  # TODO: self.options.distributed
        tc.variables["ONNX_ML"] = True
        tc.variables["HAVE_SOVERSION"] = True
        tc.variables["USE_CCACHE"] = False
        tc.variables["DEBUG_CUDA"] = self.options.get_safe("debug_cuda", False)
        tc.variables["USE_COREML_DELEGATE"] = self.options.coreml_delegate
        tc.variables["BUILD_LAZY_TS_BACKEND"] = self.options.build_lazy_ts_backend
        tc.variables["USE_MIMALLOC"] = self.options.with_mimalloc

        tc.variables["BLAS"] = self._blas_cmake_option_value

        tc.variables["MSVC_Z7_OVERRIDE"] = False

        # Custom variables for our CMake wrapper
        tc.variables["CONAN_LIBTORCH_USE_FLATBUFFERS"] = self._depends_on_flatbuffers
        tc.variables["CONAN_LIBTORCH_USE_PTHREADPOOL"] = self._depends_on_pthreadpool
        tc.variables["CONAN_LIBTORCH_USE_SLEEF"] = self._depends_on_sleef

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("cpuinfo", "cmake_target_name", "cpuinfo")
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        deps.set_property("fmt", "cmake_target_name", "fmt::fmt-header-only")
        deps.set_property("foxi", "cmake_target_name", "foxi_loader")
        deps.set_property("fp16", "cmake_target_name", "fp16")
        deps.set_property("gflags", "cmake_target_name", "gflags")
        deps.set_property("ittapi", "cmake_file_name", "ITT")
        deps.set_property("libbacktrace", "cmake_file_name", "Backtrace")
        deps.set_property("mimalloc", "cmake_target_name", "mimalloc-static")
        deps.set_property("psimd", "cmake_target_name", "psimd")
        deps.set_property("pthreadpool", "cmake_target_name", "pthreadpool")
        deps.set_property("xnnpack", "cmake_target_name", "XNNPACK")
        deps.generate()

        VirtualBuildEnv(self).generate()

        # To install pyyaml
        env = Environment()
        env.append_path("PYTHONPATH", self._site_packages_dir)
        env.append_path("PATH", os.path.join(self._site_packages_dir, "bin"))
        env.vars(self).save_script("pythonpath")

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def _pip_install(self, packages):
        self.run(f"python -m pip install {' '.join(packages)} --no-cache-dir --target={self._site_packages_dir}")

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Recreate some for add_subdirectory() to work
        for pkg in ["foxi", "fmt", "FXdiv", "psimd", "mimalloc"]:
            save(self, os.path.join(self.source_folder, "third_party", pkg, "CMakeLists.txt"), "")
        # Use FindOpenMP from Conan or CMake
        modules_dir = os.path.join(self.source_folder, "cmake", "modules")
        rm(self, "FindOpenMP.cmake", modules_dir)

    def _regenerate_flatbuffers(self):
        # Re-generate mobile_bytecode_generated.h to allow any flatbuffers version to be used.
        # As of v24.3.25, only updates the flatbuffers version in the generated file.
        self.run(f"flatc --cpp --gen-mutable --no-prefix --scoped-enums mobile_bytecode.fbs",
                 cwd=os.path.join(self.source_folder, "torch", "csrc", "jit", "serialization"))

    def build(self):
        self._patch_sources()
        self._pip_install(["pyyaml", "typing-extensions"])
        if self._depends_on_flatbuffers:
            self._regenerate_flatbuffers()
        cmake = CMake(self)
        cmake.configure()
        try:
            cmake.build()
        except Exception:
            # The build is likely to run out of memory in the CI, so try again
            cmake.build(cli_args=["--parallel", "1"])

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        os.rename(os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "res", "cmake"))

    def package_info(self):
        def _lib_exists(name):
            return bool(list(Path(self.package_folder, "lib").glob(f"*{name}.*")))

        def _add_whole_archive_lib(component, libname, shared=False):
            # Reproduces https://github.com/pytorch/pytorch/blob/v2.4.0/cmake/TorchConfig.cmake.in#L27-L43
            if shared:
                self.cpp_info.components[component].libs.append(libname)
            else:
                lib_folder = os.path.join(self.package_folder, "lib")
                if is_apple_os(self):
                    lib_fullpath = os.path.join(lib_folder, f"lib{libname}.a")
                    whole_archive = f"-Wl,-force_load,{lib_fullpath}"
                elif is_msvc(self):
                    lib_fullpath = os.path.join(lib_folder, libname)
                    whole_archive = f"-WHOLEARCHIVE:{lib_fullpath}"
                else:
                    lib_fullpath = os.path.join(lib_folder, f"lib{libname}.a")
                    whole_archive = f"-Wl,--whole-archive,{lib_fullpath},--no-whole-archive"
                self.cpp_info.components[component].exelinkflags.append(whole_archive)
                self.cpp_info.components[component].sharedlinkflags.append(whole_archive)

        def _sleef():
            return ["sleef::sleef"] if self._depends_on_sleef else []

        def _openblas():
            return ["openblas::openblas"] if self.options.blas == "openblas" else []

        def _lapack():
            return ["openblas::openblas"]

        def _openmp():
            return ["openmp::openmp"] if self.options.with_openmp else []

        def _fbgemm():
            return ["fbgemm::fbgemm"] if self.options.with_fbgemm else []

        def _gflags():
            return ["gflags::gflags"] if self.options.with_gflags else []

        def _glog():
            return ["glog::glog"] if self.options.with_glog else []

        def _nnpack():
            return []  # TODO

        def _xnnpack():
            return ["xnnpack::xnnpack"] if self.options.with_xnnpack else []

        def _libnuma():
            return ["libnuma::libnuma"] if self.options.get_safe("with_numa") else []

        def _opencl():
            return ["opencl-headers::opencl-headers", "opencl-icd-loader::opencl-icd-loader"] if self.options.with_opencl else []

        def _vulkan():
            return ["vulkan-headers::vulkan-headers", "vulkan-loader::vulkan-loader"] if self.options.with_vulkan else []

        def _onednn():
            return ["onednn::onednn"] if self.options.get_safe("with_mkldnn", False) else []

        def _mimalloc():
            return ["mimalloc::mimalloc"] if self.options.with_mimalloc else []

        def _protobuf():
            return ["protobuf::libprotobuf-lite"] if self.dependencies["protobuf"].options.lite else ["protobuf::libprotobuf"]

        def _flatbuffers():
            return ["flatbuffers::flatbuffers"] if self._depends_on_flatbuffers else []

        def _kineto():
            return []  # TODO

        def _itt():
            return ["ittapi::ittapi"] if self.options.with_itt else []

        self.cpp_info.set_property("cmake_file_name", "Torch")

        # TODO: export ATenConfig.cmake variables
        # set(ATEN_FOUND 1)
        # set(ATEN_INCLUDE_DIR "/usr/local/include")
        # set(ATEN_LIBRARIES "")
        # TODO: export Caffe2Config.cmake variables
        # set(Caffe2_MAIN_LIBS torch_library)
        # set(CAFFE2_INCLUDE_DIRS "${_INSTALL_PREFIX}/include")
        # TODO: export TorchConfig.cmake variables
        # TORCH_FOUND        -- True if the system has the Torch library
        # TORCH_INCLUDE_DIRS -- The include directories for torch
        # TORCH_LIBRARIES    -- Libraries to link against
        # TORCH_CXX_FLAGS    -- Additional (required) compiler flags

        self.cpp_info.components["_headers"].includedirs.append(os.path.join("include", "torch", "csrc", "api", "include"))
        self.cpp_info.components["_headers"].requires.extend(["onnx::onnx"] + _flatbuffers())

        self.cpp_info.components["c10"].set_property("cmake_target_name", "c10")
        self.cpp_info.components["c10"].libs = ["c10"]
        self.cpp_info.components["c10"].requires.extend(
            ["_headers", "fmt::fmt", "cpuinfo::cpuinfo", "libbacktrace::libbacktrace", "cpp-httplib::cpp-httplib"] +
            _gflags() + _glog() + _libnuma() + _mimalloc()
        )
        if self.settings.os == "Android":
            self.cpp_info.components["c10"].system_libs.append("log")

        self.cpp_info.components["torch"].set_property("cmake_target_name", "torch")
        _add_whole_archive_lib("torch", "torch", shared=self.options.shared)
        self.cpp_info.components["torch"].requires.append("torch_cpu")

        self.cpp_info.components["torch_cpu"].set_property("cmake_target_name", "torch_cpu")
        _add_whole_archive_lib("torch_cpu", "torch_cpu", shared=self.options.shared)
        self.cpp_info.components["torch_cpu"].requires.append("_headers")
        self.cpp_info.components["torch_cpu"].requires.append("c10")

        ## TODO: Eventually remove this workaround in the future
        ## We put all these external dependencies and system libs of torch_cpu in an empty component instead,
        ## due to "whole archive" trick. Indeed, conan doesn't honor libs order per component we expect in this case
        ## (conan generators put exelinkflags/sharedlinkflags after system/external libs)
        self.cpp_info.components["torch_cpu"].requires.append("torch_cpu_link_order_workaround")
        self.cpp_info.components["torch_cpu_link_order_workaround"].requires.extend(
            ["_headers", "c10", "eigen::eigen", "fmt::fmt", "foxi::foxi", "cpp-httplib::cpp-httplib"] +
            _fbgemm() + _sleef() + _onednn() + _protobuf() + _fbgemm() + _kineto() + _openblas() + _lapack() +
            _vulkan() + _opencl() + _openmp() + _nnpack() + _xnnpack() + _itt()
        )
        if self.settings.os == "Linux":
            self.cpp_info.components["torch_cpu_link_order_workaround"].system_libs.extend(["dl", "m", "pthread", "rt"])
        if self.options.blas == "veclib":
            self.cpp_info.components["torch_cpu_link_order_workaround"].frameworks.append("Accelerate")

        if self.options.shared:
            ## TODO: Eventually remove this workaround in the future
            self.cpp_info.components["torch_cpu_link_order_workaround"].requires.extend(_protobuf())
        else:
            # caffe2_protos
            _add_whole_archive_lib("libtorch_caffe2_protos", "caffe2_protos")
            self.cpp_info.components["torch_cpu"].requires.append("libtorch_caffe2_protos")
            ## TODO: Eventually remove this workaround in the future
            self.cpp_info.components["libtorch_caffe2_protos"].requires.append("libtorch_caffe2_protos_link_order_workaround")
            self.cpp_info.components["libtorch_caffe2_protos_link_order_workaround"].requires.extend(_protobuf())

            if _lib_exists("Caffe2_perfkernels_avx"):
                _add_whole_archive_lib("libtorch_caffe2_perfkernels_avx", "Caffe2_perfkernels_avx", shared=self.options.shared)
                self.cpp_info.components["libtorch_caffe2_perfkernels_avx"].requires.append("c10")
                self.cpp_info.components["torch_cpu"].requires.append("libtorch_caffe2_perfkernels_avx")

            if _lib_exists("Caffe2_perfkernels_avx2"):
                _add_whole_archive_lib("libtorch_caffe2_perfkernels_avx2", "Caffe2_perfkernels_avx2", shared=self.options.shared)
                self.cpp_info.components["libtorch_caffe2_perfkernels_avx2"].requires.append("c10")
                self.cpp_info.components["torch_cpu"].requires.append("libtorch_caffe2_perfkernels_avx2")

            if _lib_exists("Caffe2_perfkernels_avx512"):
                _add_whole_archive_lib("libtorch_caffe2_perfkernels_avx512", "Caffe2_perfkernels_avx512", shared=self.options.shared)
                self.cpp_info.components["libtorch_caffe2_perfkernels_avx512"].requires.append("c10")
                self.cpp_info.components["torch_cpu"].requires.append("libtorch_caffe2_perfkernels_avx512")

        if self.options.observers:
            _add_whole_archive_lib("libtorch_caffe2_observers", "caffe2_observers", shared=self.options.shared)
            self.cpp_info.components["libtorch_caffe2_observers"].requires.append("torch")

        if self.options.get_safe("with_qnnpack"):
            self.cpp_info.components["clog"].libs = ["clog"]

            self.cpp_info.components["libtorch_pytorch_qnnpack"].libs = ["pytorch_qnnpack"]
            self.cpp_info.components["libtorch_pytorch_qnnpack"].requires.extend([
                "clog", "cpuinfo::cpuinfo", "fp16::fp16", "fxdiv::fxdiv", "psimd::psimd", "pthreadpool::pthreadpool"
            ])
            self.cpp_info.components["torch_cpu"].requires.append("libtorch_pytorch_qnnpack")
