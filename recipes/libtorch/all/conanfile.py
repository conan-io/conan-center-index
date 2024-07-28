import glob

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

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
        "build_lazy_cuda_linalg": [True, False],
        "build_lazy_ts_backend": [True, False],
        "build_lite_interpreter": [True, False],
        "coreml_delegate": [True, False],
        "debug_cuda": [True, False],
        "fakelowp": [True, False],
        "observers": [True, False],
        "profiling": [True, False],
        "utilities": [True, False],
        "vulkan_fp16_inference": [True, False],
        "vulkan_relaxed_precision": [True, False],
        "with_cuda": [True, False],
        "with_cudnn": [True, False],
        "with_cusparselt": [True, False],
        "with_fbgemm": [True, False],
        "with_gflags": [True, False],
        "with_glog": [True, False],
        "with_magma": [True, False],
        "with_metal": [True, False],
        "with_mimalloc": [True, False],
        "with_mkldnn": [True, False],
        "with_mps": [True, False],
        "with_nccl": [True, False],
        "with_nnapi": [True, False],
        "with_nnpack": [True, False],
        "with_numa": [True, False],
        "with_nvrtc": [True, False],
        "with_opencl": [True, False],
        "with_openmp": [True, False],
        "with_qnnpack": [True, False],
        "with_rocm": [True, False],
        "with_snpe": [True, False],
        "with_vulkan": [True, False],
        "with_xnnpack": [True, False],
        "with_xpu": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "blas": "openblas",
        "build_lazy_cuda_linalg": False,
        "build_lazy_ts_backend": True,
        "build_lite_interpreter": False,
        "coreml_delegate": False,
        "debug_cuda": False,
        "fakelowp": False,
        "observers": False,
        "profiling": False,
        "utilities": False,
        "vulkan_fp16_inference": False,
        "vulkan_relaxed_precision": False,
        "with_cuda": False,
        "with_cudnn": True,
        "with_cusparselt": True,
        "with_fbgemm": False, # TODO: should be True
        "with_gflags": False,
        "with_glog": False,
        "with_magma": True,
        "with_metal": False,
        "with_mimalloc": False,
        "with_mkldnn": False,
        "with_mps": True,
        "with_nccl": True,
        "with_nnapi": False,
        "with_nnpack": False, # TODO: should be True
        "with_numa": True,
        "with_nvrtc": False,
        "with_opencl": False,
        "with_openmp": True,
        "with_qnnpack": False, # TODO: should be True
        "with_rocm": False,
        "with_snpe": False,
        "with_vulkan": False,
        "with_xnnpack": True,
        "with_xpu": False,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    @property
    def _is_mobile_os(self):
        return self.settings.os == "Android" or (is_apple_os(self) and self.settings.os != "Macos")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_nnpack
            del self.options.with_qnnpack
        if not is_apple_os(self):
            del self.options.with_metal
        if self.settings.os != "Linux":
            del self.options.with_numa
        if self.settings.os != "Android":
            del self.options.with_nnapi
            del self.options.with_snpe
        else:
            self.options.with_vulkan = True
        if self._is_mobile_os:
            self.options.blas = "eigen"
            self.options.build_lazy_ts_backend = False
        if self.settings.arch not in ["x86", "x86_64", "armv8"]:
            del self.options.with_mkldnn

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_cuda:
            self.options.rm_safe("build_lazy_cuda_linalg")
            self.options.rm_safe("debug_cuda")
            self.options.rm_safe("with_cudnn")
            self.options.rm_safe("with_cusparselt")
            self.options.rm_safe("with_nvrtc")
            if not self.options.with_rocm:
                self.options.rm_safe("with_nccl")
        if not self.options.with_vulkan:
            self.options.rm_safe("vulkan_fp16_inference")
            self.options.rm_safe("vulkan_relaxed_precision")
        if not self.options.with_fbgemm:
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
        return not is_msvc(self) and not self._is_mobile_os

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
        self.requires("cpython/3.12.2")
        self.requires("cpuinfo/cci.20231129")
        self.requires("eigen/3.4.0")
        self.requires("fmt/11.0.2")
        self.requires("foxi/cci.20210217")
        self.requires("onnx/1.16.1")
        self.requires("protobuf/3.21.12")
        if self._depends_on_sleef:
            self.requires("sleef/3.6")
        if self.options.blas == "openblas":
            self.requires("openblas/0.3.27")
        if self.options.with_openmp:
            self.requires("openmp/system")
        if self.options.with_cuda:
            self.output.warning("cuda recipe not yet available in CCI, assuming that NVIDIA CUDA SDK is installed on your system")
        if self.options.get_safe("with_cudnn"):
            self.output.warn("cudnn recipe not yet available in CCI, assuming that NVIDIA CuDNN is installed on your system")
        if self.options.with_rocm:
            raise ConanInvalidConfiguration("rocm recipe not yet available in CCI")
        if self.options.with_fbgemm:
            self.requires("fbgemm/0.8.0")
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_glog:
            self.requires("glog/0.7.1")
        if self.options.get_safe("with_nnpack"):
            raise ConanInvalidConfiguration("nnpack recipe not yet available in CCI")
        if self.options.get_safe("with_qnnpack"):
            self.requires("fp16/cci.20200514")
            self.requires("fxdiv/cci.20200417")
            self.requires("psimd/cci.20200517")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20240229")
        if self._use_nnpack_family:
            self.requires("pthreadpool/cci.20231129")
        if self.options.get_safe("with_numa"):
            self.requires("libnuma/2.0.16")
        if self.options.with_opencl:
            self.requires("opencl-headers/2023.12.14")
            self.requires("opencl-icd-loader/2023.12.14")
        if self.options.with_vulkan:
            self.requires("vulkan-headers/1.3.268.0")
            self.requires("vulkan-loader/1.3.268.0")

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
        if self.options.blas == "veclib" and not is_apple_os(self):
            raise ConanInvalidConfiguration("veclib only available on Apple family OS")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")
        # FIXME: libtorch 1.8.0 requires:
        #  - python 3.6.2+ with pyyaml, dataclasses and typing_extensions libs
        #  or
        #  - python 3.7+ with pyyaml and typing_extensions libs
        #  or
        #  - python 3.8+ with pyyaml lib
        # self.build_requires("cpython/3.9.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TEST"] = False
        tc.variables["ATEN_NO_TEST"] = True
        tc.variables["BUILD_BINARY"] = self.options.utilities
        tc.variables["BUILD_CUSTOM_PROTOBUF"] = False
        tc.variables["BUILD_PYTHON"] = False
        tc.variables["BUILD_LITE_INTERPRETER"] = self.options.build_lite_interpreter
        tc.variables["CAFFE2_USE_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.variables["USE_CUDA"] = self.options.with_cuda
        tc.variables["USE_XPU"] = self.options.with_xpu
        tc.variables["BUILD_LAZY_CUDA_LINALG"] = self.options.get_safe("build_lazy_cuda_linalg", False)
        tc.variables["USE_ROCM"] = self.options.with_rocm
        tc.variables["CAFFE2_STATIC_LINK_CUDA"] = False
        tc.variables["USE_CUDNN"] = self.options.get_safe("with_cudnn", False)
        tc.variables["USE_STATIC_CUDNN"] = False
        tc.variables["USE_CUSPARSELT"] = self.options.get_safe("with_cusparselt", False)
        tc.variables["USE_FBGEMM"] = self.options.with_fbgemm
        tc.variables["USE_KINETO"] = False
        tc.variables["USE_CUPTI_SO"] = True
        tc.variables["USE_FAKELOWP"] = self.options.get_safe("fakelowp", False)
        tc.variables["USE_GFLAGS"] = self.options.with_gflags
        tc.variables["USE_GLOG"] = self.options.with_glog
        tc.variables["USE_LITE_PROTO"] = self.dependencies["protobuf"].options.lite
        tc.variables["USE_MAGMA"] = self.options.with_magma
        tc.variables["USE_PYTORCH_METAL"] = self.options.get_safe("with_metal", False)
        tc.variables["USE_PYTORCH_METAL_EXPORT"] = self.options.get_safe("with_metal", False)
        tc.variables["USE_NATIVE_ARCH"] = False
        tc.variables["USE_MPS"] = self.options.get_safe("with_mps", False)
        tc.variables["USE_NCCL"] = self.options.get_safe("with_nccl", False)
        tc.variables["USE_RCCL"] = self.options.get_safe("with_nccl", False)
        tc.variables["USE_STATIC_NCCL"] = False
        tc.variables["USE_SYSTEM_NCCL"] = False # technically we could create a recipe for nccl with 0 packages (because it requires CUDA at build time)
        tc.variables["USE_NNAPI"] = self.options.get_safe("with_nnapi", False)
        tc.variables["USE_NNPACK"] = self.options.get_safe("with_nnpack", False)
        tc.variables["USE_NUMA"] = self.options.get_safe("with_numa", False)
        tc.variables["USE_NVRTC"] = self.options.get_safe("with_nvrtc", False)
        tc.variables["USE_NUMPY"] = False
        tc.variables["USE_OBSERVERS"] = self.options.observers
        tc.variables["USE_OPENCL"] = self.options.with_opencl
        tc.variables["USE_OPENMP"] = self.options.with_openmp
        tc.variables["USE_PROF"] = self.options.profiling
        tc.variables["USE_PYTORCH_QNNPACK"] = self.options.get_safe("with_qnnpack", False) # is archived, so prefer to use vendored QNNPACK
        tc.variables["USE_SNPE"] = self.options.get_safe("with_snpe", False)
        tc.variables["USE_SYSTEM_EIGEN_INSTALL"] = True
        tc.variables["USE_VALGRIND"] = False
        tc.variables["USE_VULKAN"] = self.options.with_vulkan
        tc.variables["USE_VULKAN_FP16_INFERENCE"] = self.options.get_safe("vulkan_fp16_inference", False)
        tc.variables["USE_VULKAN_RELAXED_PRECISION"] = self.options.get_safe("vulkan_relaxed_precision", False)
        tc.variables["USE_XNNPACK"] = self.options.with_xnnpack
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
        tc.variables["CONAN_LIBTORCH_USE_SLEEF"] = self._depends_on_sleef
        tc.variables["CONAN_LIBTORCH_USE_PTHREADPOOL"] = self._use_nnpack_family

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        # apply_conandata_patches(self)
        pass

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # TODO: Keep share/Aten/Declarations.yml?
        # rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Torch")
        self.cpp_info.set_property("cmake_target_name", "Torch::Torch")

        def _lib_exists(name):
            return bool(glob.glob(os.path.join(self.package_folder, "lib", f"*{name}.*")))

        def _add_whole_archive_lib(component, libname, shared=False):
            if shared:
                self.cpp_info.components[component].libs.append(libname)
            else:
                lib_folder = os.path.join(self.package_folder, "lib")
                if is_apple_os(self):
                    lib_fullpath = os.path.join(lib_folder, f"lib{libname}.a")
                    whole_archive = "-Wl,-force_load,{}".format(lib_fullpath)
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

        def _openmp():
            return ["openmp::openmp"] if self.options.with_openmp else []

        def _fbgemm():
            return ["fbgemm::fbgemm"] if self.options.with_fbgemm else []

        def _gflags():
            return ["gflags::gflags"] if self.options.with_gflags else []

        def _glog():
            return ["glog::glog"] if self.options.with_glog else []

        def _nnpack():
            return ["nnpack::nnpack"] if self.options.get_safe("with_nnpack") else []

        def _xnnpack():
            return ["xnnpack::xnnpack"] if self.options.with_xnnpack else []

        def _pthreadpool():
            return ["pthreadpool::pthreadpool"] if self._use_nnpack_family else []

        def _libnuma():
            return ["libnuma::libnuma"] if self.options.get_safe("with_numa") else []

        def _opencl():
            return ["opencl-headers::opencl-headers", "opencl-icd-loader::opencl-icd-loader"] if self.options.with_opencl else []

        def _vulkan():
            return ["vulkan-headers::vulkan-headers", "vulkan-loader::vulkan-loader"] if self.options.with_vulkan else []

        def _onednn():
            return ["onednn::onednn"] if self.options.with_mkldnn else []

        # torch
        _add_whole_archive_lib("_libtorch", "torch", shared=self.options.shared)
        self.cpp_info.components["_libtorch"].requires.append("libtorch_cpu")

        # torch_cpu
        _add_whole_archive_lib("libtorch_cpu", "torch_cpu", shared=self.options.shared)
        self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_c10")

        ## TODO: Eventually remove this workaround in the future
        ## We put all these external dependencies and system libs of torch_cpu in an empty component instead,
        ## due to "whole archive" trick. Indeed, conan doesn't honor libs order per component we expect in this case
        ## (conan generators put exelinkflags/sharedlinkflags after system/external libs)
        self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_cpu_link_order_workaround")
        self.cpp_info.components["libtorch_cpu_link_order_workaround"].requires.extend(
            ["cpuinfo::cpuinfo", "eigen::eigen", "foxi::foxi"] +
            _openblas() + _onednn() + _sleef() + _openmp() + _vulkan()
        )
        if self.settings.os == "Linux":
            self.cpp_info.components["libtorch_cpu_link_order_workaround"].system_libs.extend(["dl", "m", "pthread", "rt"])
        if self.options.blas == "veclib":
            self.cpp_info.components["libtorch_cpu_link_order_workaround"].frameworks.append("Accelerate")

        # c10
        self.cpp_info.components["libtorch_c10"].libs = ["c10"]
        self.cpp_info.components["libtorch_c10"].requires.extend(
            _gflags() + _glog() + _libnuma()
        )
        if self.settings.os == "Android":
            self.cpp_info.components["libtorch_c10"].system_libs.append("log")

        ##------------------
        ## FIXME: let's put all build modules, include dirs, external dependencies (except protobuf) and system/frameworks libs in c10 for the moment
        self.cpp_info.components["libtorch_c10"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["libtorch_c10"].includedirs.append(os.path.join("include", "torch", "csrc", "api", "include"))
        self.cpp_info.components["libtorch_c10"].requires.extend(["fmt::fmt", "onnx::onnx"])
        self.cpp_info.components["libtorch_c10"].requires.extend(
            _openmp() + _fbgemm() + _nnpack() + _xnnpack() + _pthreadpool() + _opencl()
        )
        ##------------------

        if self.options.shared:
            ## TODO: Eventually remove this workaround in the future
            self.cpp_info.components["libtorch_cpu_link_order_workaround"].requires.append("protobuf::protobuf")
        else:
            # caffe2_protos
            _add_whole_archive_lib("libtorch_caffe2_protos", "caffe2_protos")
            self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_caffe2_protos")
            ## TODO: Eventually remove this workaround in the future
            self.cpp_info.components["libtorch_caffe2_protos"].requires.append("libtorch_caffe2_protos_link_order_workaround")
            self.cpp_info.components["libtorch_caffe2_protos_link_order_workaround"].requires.append("protobuf::protobuf")

            # Caffe2_perfkernels_avx
            if _lib_exists("Caffe2_perfkernels_avx"):
                _add_whole_archive_lib("libtorch_caffe2_perfkernels_avx", "Caffe2_perfkernels_avx", shared=self.options.shared)
                self.cpp_info.components["libtorch_caffe2_perfkernels_avx"].requires.append("libtorch_c10")
                self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_caffe2_perfkernels_avx")

            # Caffe2_perfkernels_avx2
            if _lib_exists("Caffe2_perfkernels_avx2"):
                _add_whole_archive_lib("libtorch_caffe2_perfkernels_avx2", "Caffe2_perfkernels_avx2", shared=self.options.shared)
                self.cpp_info.components["libtorch_caffe2_perfkernels_avx2"].requires.append("libtorch_c10")
                self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_caffe2_perfkernels_avx2")

            # Caffe2_perfkernels_avx512
            if _lib_exists("Caffe2_perfkernels_avx512"):
                _add_whole_archive_lib("libtorch_caffe2_perfkernels_avx512", "Caffe2_perfkernels_avx512", shared=self.options.shared)
                self.cpp_info.components["libtorch_caffe2_perfkernels_avx512"].requires.append("libtorch_c10")
                self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_caffe2_perfkernels_avx512")

        # caffe2_observers
        if self.options.observers:
            _add_whole_archive_lib("libtorch_caffe2_observers", "caffe2_observers", shared=self.options.shared)
            self.cpp_info.components["libtorch_caffe2_observers"].requires.append("_libtorch")

        # c10d
        if self.options.distributed:
            self.cpp_info.components["libtorch_c10d"].libs = ["c10d"] # always static
            self.cpp_info.components["libtorch_c10d"].requires.extend(["_libtorch"])

        # process_group_agent & tensorpipe_agent
        if self.options.get_safe("with_tensorpipe"):
            self.cpp_info.components["libtorch_process_group_agent"].libs = ["process_group_agent"]
            self.cpp_info.components["libtorch_process_group_agent"].requires.extend(["_libtorch", "libtorch_c10d"])
            self.cpp_info.components["libtorch_tensorpipe_agent"].libs = ["tensorpipe_agent"]
            self.cpp_info.components["libtorch_tensorpipe_agent"].requires.extend(["_libtorch", "libtorch_c10d", "fmt::fmt"])

        # caffe2_nvrtc
        if self.options.with_cuda or self.options.with_rocm:
            self.cpp_info.components["libtorch_caffe2_nvrtc"].libs = ["caffe2_nvrtc"]

        if self.options.with_cuda:
            # torch_cuda
            _add_whole_archive_lib("libtorch_torch_cuda", "torch_cuda", shared=self.options.shared)
            self.cpp_info.components["libtorch_torch_cuda"].requires.append("libtorch_c10_cuda")
            self.cpp_info.components["_libtorch"].requires.append("libtorch_torch_cuda")

            # c10_cuda
            self.cpp_info.components["libtorch_c10_cuda"].libs = ["c10_cuda"]
            self.cpp_info.components["libtorch_c10_cuda"].requires.append("libtorch_c10")

            # caffe2_detectron_ops_gpu
            if self.options.shared:
                self.cpp_info.components["libtorch_caffe2_detectron_ops_gpu"].libs = ["caffe2_detectron_ops_gpu"]
                self.cpp_info.components["libtorch_caffe2_detectron_ops_gpu"].requires.extend(["_libtorch", "libtorch_cpu", "libtorch_c10"])
        elif self.options.with_rocm:
            # torch_hip
            _add_whole_archive_lib("libtorch_torch_hip", "torch_hip", shared=self.options.shared)
            self.cpp_info.components["libtorch_torch_hip"].requires.append("libtorch_c10_hip")
            self.cpp_info.components["_libtorch"].requires.append("libtorch_torch_hip")

            # c10_hip
            self.cpp_info.components["libtorch_c10_hip"].libs = ["c10_hip"]
            self.cpp_info.components["libtorch_c10_hip"].requires.append("libtorch_c10")

            # caffe2_detectron_ops_hip
            if self.options.shared:
                self.cpp_info.components["libtorch_caffe2_detectron_ops_hip"].libs = ["caffe2_detectron_ops_hip"]
                self.cpp_info.components["libtorch_caffe2_detectron_ops_hip"].requires.extend(["_libtorch", "libtorch_cpu", "libtorch_c10"])
        elif not self.settings.os == "iOS":
            # caffe2_detectron_ops
            if self.options.shared:
                self.cpp_info.components["libtorch_caffe2_detectron_ops"].libs = ["caffe2_detectron_ops"]
                self.cpp_info.components["libtorch_caffe2_detectron_ops"].requires.extend(["_libtorch", "libtorch_cpu", "libtorch_c10"])

        # pytorch_qnnpack
        if self.options.get_safe("with_qnnpack"):
            self.cpp_info.components["libtorch_pytorch_qnnpack"].libs = ["pytorch_qnnpack"]
            self.cpp_info.components["libtorch_pytorch_qnnpack"].requires.extend([
                "cpuinfo::cpuinfo", "fp16::fp16", "fxdiv::fxdiv", "psimd::psimd", "pthreadpool::pthreadpool"
            ])
            self.cpp_info.components["libtorch_cpu"].requires.append("libtorch_pytorch_qnnpack")

        if self.options.utilities:
            bin_path = os.path.join(self.package_folder, "bin")
            self.env_info.PATH.append(bin_path)
