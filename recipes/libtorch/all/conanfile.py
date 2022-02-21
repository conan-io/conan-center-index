from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import textwrap

required_conan_version = ">=1.33.0"


class LibtorchConan(ConanFile):
    name = "libtorch"
    description = "Tensors and Dynamic neural networks with strong GPU acceleration."
    license = "BSD-3-Clause"
    topics = ("conan", "libtorch", "pytorch", "machine-learning",
              "deep-learning", "neural-network", "gpu", "tensor")
    homepage = "https://pytorch.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "blas": ["eigen", "atlas", "openblas", "mkl", "veclib", "flame", "generic"], # generic means "whatever blas lib found"
        "aten_parallel_backend": ["native", "openmp", "tbb"],
        "with_cuda": [True, False],
        "with_cudnn": [True, False],
        "with_nvrtc": [True, False],
        "with_tensorrt": [True, False],
        "with_kineto": [True, False],
        "with_rocm": [True, False],
        "with_nccl": [True, False],
        "with_fbgemm": [True, False],
        "fakelowp": [True, False],
        "with_ffmpeg": [True, False],
        "with_gflags": [True, False],
        "with_glog": [True, False],
        "with_leveldb": [True, False],
        "with_lmdb": [True, False],
        "with_metal": [True, False],
        "with_nnapi": [True, False],
        "with_nnpack": [True, False],
        "with_numa": [True, False],
        "observers": [True, False],
        "with_opencl": [True, False],
        "with_opencv": [True, False],
        "profiling": [True, False],
        "with_qnnpack": [True, False],
        "with_redis": [True, False],
        "with_rocksdb": [True, False],
        "with_snpe": [True, False],
        "with_vulkan": [True, False],
        "vulkan_shaderc_runtime": [True, False],
        "vulkan_relaxed_precision": [True, False],
        "with_xnnpack": [True, False],
        "with_zmq": [True, False],
        "with_zstd": [True, False],
        "with_mkldnn": [True, False],
        "distributed": [True, False],
        "with_mpi": [True, False],
        "with_gloo": [True, False],
        "with_tensorpipe": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "blas": "openblas", # TODO: should be mkl on non mobile os
        "aten_parallel_backend": "native",
        "with_cuda": False,
        "with_cudnn": True,
        "with_nvrtc": False,
        "with_tensorrt": False,
        "with_kineto": False, # TODO: should be True
        "with_rocm": False,
        "with_nccl": True,
        "with_fbgemm": False, # TODO: should be True
        "fakelowp": False,
        "with_ffmpeg": False,
        "with_gflags": False,
        "with_glog": False,
        "with_leveldb": False,
        "with_lmdb": False,
        "with_metal": True,
        "with_nnapi": False,
        "with_nnpack": False, # TODO: should be True
        "with_qnnpack": True,
        "with_xnnpack": True,
        "with_numa": True,
        "observers": False,
        "with_opencl": False,
        "with_opencv": False,
        "profiling": False,
        "with_redis": False,
        "with_rocksdb": False,
        "with_snpe": False,
        "with_vulkan": False,
        "vulkan_shaderc_runtime": False,
        "vulkan_relaxed_precision": False,
        "with_zmq": False,
        "with_zstd": False,
        "with_mkldnn": False,
        "distributed": True,
        "with_mpi": True,
        "with_gloo": False, # TODO: should be True
        "with_tensorpipe": True,
        "utilities": False,
    }

    short_paths = True

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        # Change default options for several OS
        if self.settings.os in ["Android", "iOS"]:
            self.options.blas = "eigen"
        if self.settings.os not in ["Linux", "Windows"]:
            self.options.distributed = False

        # Remove several options not supported for several OS
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_nnpack
            del self.options.with_qnnpack
            del self.options.with_mpi
            del self.options.with_tensorpipe
            del self.options.with_kineto
        if self.settings.os != "iOS":
            del self.options.with_metal
        if self.settings.os != "Android":
            del self.options.with_nnapi
            del self.options.with_snpe
        if self.settings.os != "Linux":
            del self.options.with_numa

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_cuda:
            del self.options.with_cudnn
            del self.options.with_nvrtc
            del self.options.with_tensorrt
            del self.options.with_kineto
        if not (self.options.with_cuda or self.options.with_rocm):
            del self.options.with_nccl
        if not self.options.with_vulkan:
            del self.options.vulkan_shaderc_runtime
            del self.options.vulkan_relaxed_precision
        if not self.options.with_fbgemm:
            del self.options.fakelowp
        if not self.options.distributed:
            del self.options.with_mpi
            del self.options.with_gloo
            del self.options.with_tensorpipe

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        if self.options.with_cuda and self.options.with_rocm:
            raise ConanInvalidConfiguration("libtorch doesn't yet support simultaneously building with CUDA and ROCm")
        if self.options.with_ffmpeg and not self.options.with_opencv:
            raise ConanInvalidConfiguration("libtorch video support with ffmpeg also requires opencv")
        if self.options.blas == "veclib" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("veclib only available on Apple family OS")
        if self.settings.os == "Linux" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration("clang with libc++ can't build libtorch") # TODO: try to fix that

        if self.options.distributed and self.settings.os not in ["Linux", "Windows"]:
            self.output.warn("Distributed libtorch is not tested on {} and likely won't work".format(str(self.settings.os)))

        # numa static can't be linked into shared libs.
        # Because Caffe2_detectron_ops* libs are always shared, we have to force
        # libnuma shared even if libtorch:shared=False
        if self.options.get_safe("with_numa"):
            self.options["libnuma"].shared = True

    def requirements(self):
        self.requires("cpuinfo/cci.20201217")
        self.requires("eigen/3.3.9")
        self.requires("fmt/7.1.3")
        self.requires("foxi/cci.20210217")
        self.requires("onnx/1.8.1")
        self.requires("protobuf/3.17.1")
        if self._depends_on_sleef:
            self.requires("sleef/3.5.1")
        if self.options.blas == "openblas":
            self.requires("openblas/0.3.13")
        elif self.options.blas in ["atlas", "mkl", "flame"]:
            raise ConanInvalidConfiguration("{} recipe not yet available in CCI".format(self.options.blas))
        if self.options.aten_parallel_backend == "tbb":
            self.requires("tbb/2020.3")
        if self.options.with_cuda:
            self.output.warn("cuda recipe not yet available in CCI, assuming that NVIDIA CUDA SDK is installed on your system")
        if self.options.get_safe("with_cudnn"):
            self.output.warn("cudnn recipe not yet available in CCI, assuming that NVIDIA CuDNN is installed on your system")
        if self.options.get_safe("with_tensorrt"):
            self.output.warn("tensorrt recipe not yet available in CCI, assuming that NVIDIA TensorRT SDK is installed on your system")
        if self.options.get_safe("with_kineto"):
            raise ConanInvalidConfiguration("kineto recipe not yet available in CCI")
        if self.options.with_rocm:
            raise ConanInvalidConfiguration("rocm recipe not yet available in CCI")
        if self.options.with_fbgemm:
            raise ConanInvalidConfiguration("fbgemm recipe not yet available in CCI")
            self.requires("fbgemm/cci.20210309")
        if self.options.with_ffmpeg:
            raise ConanInvalidConfiguration("ffmpeg recipe not yet available in CCI")
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_glog:
            self.requires("glog/0.4.0")
        if self.options.with_leveldb:
            self.requires("leveldb/1.22")
        if self.options.with_lmdb:
            # should be part of OpenLDAP or packaged separately?
            raise ConanInvalidConfiguration("lmdb recipe not yet available in CCI")
        if self.options.get_safe("with_nnpack"):
            raise ConanInvalidConfiguration("nnpack recipe not yet available in CCI")
        if self.options.get_safe("with_qnnpack"):
            self.requires("fp16/cci.20200514")
            self.requires("fxdiv/cci.20200417")
            self.requires("psimd/cci.20200517")
        if self.options.with_xnnpack:
            self.requires("xnnpack/cci.20211210")
        if self.options.get_safe("with_nnpack") or self.options.get_safe("with_qnnpack") or self.options.with_xnnpack:
            self.requires("pthreadpool/cci.20210218")
        if self.options.get_safe("with_numa"):
            self.requires("libnuma/2.0.14")
        if self.options.with_opencl:
            self.requires("opencl-headers/2020.06.16")
            self.requires("opencl-icd-loader/2020.06.16")
        if self.options.with_opencv:
            self.requires("opencv/4.5.1")
        if self.options.with_redis:
            self.requires("hiredis/1.0.0")
        if self.options.with_rocksdb:
            self.requires("rocksdb/6.10.2")
        if self.options.with_vulkan:
            self.requires("vulkan-headers/1.2.170.0")
            self.requires("vulkan-loader/1.2.170.0")
        if self.options.get_safe("vulkan_shaderc_runtime"):
            self.requires("shaderc/2019.0")
        if self.options.with_zmq:
            self.requires("zeromq/4.3.4")
        if self.options.with_zstd:
            self.requires("zstd/1.4.9")
        if self.options.with_mkldnn:
            raise ConanInvalidConfiguration("oneDNN (MKL-DNN) recipe not yet available in CCI")
        if self.options.get_safe("with_mpi"):
            self.requires("openmpi/4.1.0")
        if self.options.get_safe("with_gloo"):
            raise ConanInvalidConfiguration("gloo recipe not yet available in CCI")
        if self.options.get_safe("with_tensorpipe"):
            self.requires("tensorpipe/cci.20210316")

    @property
    def _depends_on_sleef(self):
        return self.settings.compiler != "Visual Studio" and self.settings.os not in ["Android", "iOS"]

    def validate(self):
        if self.options.get_safe("with_numa") and not self.options["libnuma"].shared:
            raise ConanInvalidConfiguration("libtorch requires libnuma shared. Set libnuma:shared=True, or disable " \
                                            "numa with libtorch:with_numa=False")

    def build_requirements(self):
        if self.options.with_vulkan and not self.options.vulkan_shaderc_runtime:
            self.build_requires("shaderc/2019.0")
        # FIXME: libtorch 1.8.0 requires:
        #  - python 3.6.2+ with pyyaml, dataclasses and typing_extensions libs
        #  or
        #  - python 3.7+ with pyyaml and typing_extensions libs
        #  or
        #  - python 3.8+ with pyyaml lib
        # self.build_requires("cpython/3.9.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pytorch-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ATEN_NO_TEST"] = True
        self._cmake.definitions["BUILD_BINARY"] = self.options.utilities
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_CUSTOM_PROTOBUF"] = False
        self._cmake.definitions["BUILD_PYTHON"] = False
        self._cmake.definitions["BUILD_CAFFE2"] = True
        self._cmake.definitions["BUILD_CAFFE2_OPS"] = True
        self._cmake.definitions["BUILD_CAFFE2_MOBILE"] = False
        self._cmake.definitions["CAFFE2_LINK_LOCAL_PROTOBUF"] = False
        self._cmake.definitions["CAFFE2_USE_MSVC_STATIC_RUNTIME"] = self.settings.compiler.get_safe("runtime") in ["MT", "MTd", "static"]
        self._cmake.definitions["BUILD_TEST"] = False
        self._cmake.definitions["BUILD_STATIC_RUNTIME_BENCHMARK"] = False
        self._cmake.definitions["BUILD_MOBILE_BENCHMARKS"] = False
        self._cmake.definitions["BUILD_MOBILE_TEST"] = False
        self._cmake.definitions["BUILD_JNI"] = False
        self._cmake.definitions["BUILD_MOBILE_AUTOGRAD"] = False
        self._cmake.definitions["INSTALL_TEST"] = False
        self._cmake.definitions["USE_CPP_CODE_COVERAGE"] = False
        self._cmake.definitions["COLORIZE_OUTPUT"] = True
        self._cmake.definitions["USE_ASAN"] = False
        self._cmake.definitions["USE_TSAN"] = False
        self._cmake.definitions["USE_CUDA"] = self.options.with_cuda
        self._cmake.definitions["USE_ROCM"] = self.options.with_rocm
        self._cmake.definitions["CAFFE2_STATIC_LINK_CUDA"] = False
        self._cmake.definitions["USE_CUDNN"] = self.options.get_safe("with_cudnn", False)
        self._cmake.definitions["USE_STATIC_CUDNN"] = False
        self._cmake.definitions["USE_FBGEMM"] = self.options.with_fbgemm
        self._cmake.definitions["USE_KINETO"] = self.options.get_safe("with_kineto", False)
        self._cmake.definitions["USE_FAKELOWP"] = self.options.get_safe("fakelowp", False)
        self._cmake.definitions["USE_FFMPEG"] = self.options.with_ffmpeg
        self._cmake.definitions["USE_GFLAGS"] = self.options.with_gflags
        self._cmake.definitions["USE_GLOG"] = self.options.with_glog
        self._cmake.definitions["USE_LEVELDB"] = self.options.with_leveldb
        self._cmake.definitions["USE_LITE_PROTO"] = False
        self._cmake.definitions["USE_LMDB"] = self.options.with_lmdb
        self._cmake.definitions["USE_METAL"] = self.options.get_safe("with_metal", False)
        self._cmake.definitions["USE_NATIVE_ARCH"] = False
        self._cmake.definitions["USE_NCCL"] = self.options.get_safe("with_nccl", False)
        self._cmake.definitions["USE_STATIC_NCCL"] = False
        self._cmake.definitions["USE_SYSTEM_NCCL"] = False # technically we could create a recipe for nccl with 0 packages (because it requires CUDA at build time)
        self._cmake.definitions["USE_NNAPI"] = self.options.get_safe("with_nnapi", False)
        self._cmake.definitions["USE_NNPACK"] = self.options.get_safe("with_nnpack", False)
        self._cmake.definitions["USE_NUMA"] = self.options.get_safe("with_numa", False)
        self._cmake.definitions["USE_NVRTC"] = self.options.get_safe("with_nvrtc", False)
        self._cmake.definitions["USE_NUMPY"] = False
        self._cmake.definitions["USE_OBSERVERS"] = self.options.observers
        self._cmake.definitions["USE_OPENCL"] = self.options.with_opencl
        self._cmake.definitions["USE_OPENCV"] = self.options.with_opencv
        self._cmake.definitions["USE_OPENMP"] = self.options.aten_parallel_backend == "openmp"
        self._cmake.definitions["USE_PROF"] = self.options.profiling
        self._cmake.definitions["USE_QNNPACK"] = False                                                # QNNPACK is now integrated into libtorch and official repo
        self._cmake.definitions["USE_PYTORCH_QNNPACK"] = self.options.get_safe("with_qnnpack", False) # is archived, so prefer to use vendored QNNPACK
        self._cmake.definitions["USE_REDIS"] = self.options.with_redis
        self._cmake.definitions["USE_ROCKSDB"] = self.options.with_rocksdb
        self._cmake.definitions["USE_SNPE"] = self.options.get_safe("with_snpe", False)
        self._cmake.definitions["USE_SYSTEM_EIGEN_INSTALL"] = True
        self._cmake.definitions["USE_TENSORRT"] = self.options.get_safe("with_tensorrt", False)
        self._cmake.definitions["USE_VULKAN"] = self.options.with_vulkan
        self._cmake.definitions["USE_VULKAN_WRAPPER"] = False
        self._cmake.definitions["USE_VULKAN_SHADERC_RUNTIME"] = self.options.get_safe("vulkan_shaderc_runtime", False)
        self._cmake.definitions["USE_VULKAN_RELAXED_PRECISION"] = self.options.get_safe("vulkan_relaxed_precision", False)
        self._cmake.definitions["USE_XNNPACK"] = self.options.with_xnnpack
        self._cmake.definitions["USE_ZMQ"] = self.options.with_zmq
        self._cmake.definitions["USE_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["USE_MKLDNN"] = self.options.with_mkldnn
        self._cmake.definitions["USE_MKLDNN_CBLAS"] = False # This option has no logic and is useless in libtorch actually
        self._cmake.definitions["USE_DISTRIBUTED"] = self.options.distributed
        self._cmake.definitions["USE_MPI"] = self.options.get_safe("with_mpi", False)
        self._cmake.definitions["USE_GLOO"] = self.options.get_safe("with_gloo", False)
        self._cmake.definitions["USE_TENSORPIPE"] = self.options.get_safe("with_tensorpipe", False)
        self._cmake.definitions["USE_TBB"] = self.options.aten_parallel_backend == "tbb"
        self._cmake.definitions["ONNX_ML"] = True
        self._cmake.definitions["HAVE_SOVERSION"] = True
        self._cmake.definitions["USE_SYSTEM_LIBS"] = True

        self._cmake.definitions["USE_LAPACK"] = False # TODO: add an option

        self._cmake.definitions["BUILDING_WITH_TORCH_LIBS"] = True
        self._cmake.definitions["BLAS"] = self._blas_cmake_option_value

        self._cmake.definitions["MSVC_Z7_OVERRIDE"] = False

        # Custom variables for our CMake wrapper
        self._cmake.definitions["CONAN_LIBTORCH_USE_SLEEF"] = self._depends_on_sleef
        self._cmake.definitions["CONAN_LIBTORCH_USE_PTHREADPOOL"] = self._use_nnpack_family

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

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
        return self.options.get_safe("with_nnpack") or self.options.get_safe("with_qnnpack") or self.options.with_xnnpack

    def build(self):
        if self.options.get_safe("with_snpe"):
            self.output.warn("with_snpe is enabled. Pay attention that you should have properly set SNPE_LOCATION and SNPE_HEADERS CMake variables")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # conflict with macros.h generated at build time
        os.remove(os.path.join(self.build_folder, self._source_subfolder, "caffe2", "core", "macros.h"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # TODO: Keep share/Aten/Declarations.yml?
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            if(DEFINED Torch_FOUND)
                set(TORCH_FOUND ${Torch_FOUND})
            endif()
            if(NOT DEFINED TORCH_INCLUDE_DIRS)
                get_target_property(TORCH_INCLUDE_DIRS Torch::Torch INTERFACE_INCLUDE_DIRECTORIES)
            endif()
            if(NOT DEFINED TORCH_LIBRARIES)
                set(TORCH_LIBRARIES "Torch::Torch")
            endif()
        """)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-variables.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Torch"
        self.cpp_info.names["cmake_find_package_multi"] = "Torch"

        def _lib_exists(name):
            return True if glob.glob(os.path.join(self.package_folder, "lib", "*{}.*".format(name))) else False

        def _add_whole_archive_lib(component, libname, shared=False):
            if shared:
                self.cpp_info.components[component].libs.append(libname)
            else:
                lib_folder = os.path.join(self.package_folder, "lib")
                if self.settings.os == "Macos":
                    lib_fullpath = os.path.join(lib_folder, "lib{}.a".format(libname))
                    whole_archive = "-Wl,-force_load,{}".format(lib_fullpath)
                elif self.settings.compiler == "Visual Studio":
                    lib_fullpath = os.path.join(lib_folder, "{}".format(libname))
                    whole_archive = "-WHOLEARCHIVE:{}".format(lib_fullpath)
                else:
                    lib_fullpath = os.path.join(lib_folder, "lib{}.a".format(libname))
                    whole_archive = "-Wl,--whole-archive,{},--no-whole-archive".format(lib_fullpath)
                self.cpp_info.components[component].exelinkflags.append(whole_archive)
                self.cpp_info.components[component].sharedlinkflags.append(whole_archive)

        def _sleef():
            return ["sleef::sleef"] if self._depends_on_sleef else []

        def _openblas():
            return ["openblas::openblas"] if self.options.blas == "openblas" else []

        def _tbb():
            return ["tbb::tbb"] if self.options.aten_parallel_backend == "tbb" else []

        def _fbgemm():
            return ["fbgemm::fbgemm"] if self.options.with_fbgemm else []

        def _ffmpeg():
            return ["ffmpeg::ffmpeg"] if self.options.with_ffmpeg else []

        def _gflags():
            return ["gflags::gflags"] if self.options.with_gflags else []

        def _glog():
            return ["glog::glog"] if self.options.with_glog else []

        def _leveldb():
            return ["leveldb::leveldb"] if self.options.with_leveldb else []

        def _nnpack():
            return ["nnpack::nnpack"] if self.options.get_safe("with_nnpack") else []

        def _xnnpack():
            return ["xnnpack::xnnpack"] if self.options.with_xnnpack else []

        def _pthreadpool():
            return ["pthreadpool::pthreadpool"] if self.options.get_safe("with_nnpack") or self.options.get_safe("with_qnnpack") or self.options.with_xnnpack else []

        def _libnuma():
            return ["libnuma::libnuma"] if self.options.get_safe("with_numa") else []

        def _opencl():
            return ["opencl-headers::opencl-headers", "opencl-icd-loader::opencl-icd-loader"] if self.options.with_opencl else []

        def _opencv():
            return ["opencv::opencv"] if self.options.with_opencv else []

        def _redis():
            return ["hiredis::hiredis"] if self.options.with_redis else []

        def _vulkan():
            return ["vulkan-headers::vulkan-headers", "vulkan-loader::vulkan-loader"] if self.options.with_vulkan else []

        def _shaderc():
            return ["shaderc::shaderc"] if self.options.get_safe("vulkan_shaderc_runtime") else []

        def _zeromq():
            return ["zeromq::zeromq"] if self.options.with_zmq else []

        def _zstd():
            return ["zstd::zstd"] if self.options.with_zstd else []

        def _onednn():
            return ["onednn::onednn"] if self.options.with_mkldnn else []

        def _openmpi():
            return ["openmpi::openmpi"] if self.options.get_safe("with_mpi") else []

        def _gloo():
            return ["gloo::gloo"] if self.options.get_safe("with_gloo") else []

        def _tensorpipe():
            return ["tensorpipe::tensorpipe"] if self.options.get_safe("with_tensorpipe") else []

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
            _openblas() + _onednn() + _sleef() + _leveldb() + _openmpi() +
            _gloo() + _redis() + _zstd() + _tensorpipe() + _opencv() +
            _vulkan() + _shaderc() + _zeromq() + _ffmpeg()
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
        self.cpp_info.components["libtorch_c10"].build_modules["cmake_find_package"] = [os.path.join(self._module_subfolder, self._module_file)]
        self.cpp_info.components["libtorch_c10"].build_modules["cmake_find_package_multi"] = [os.path.join(self._module_subfolder, self._module_file)]
        self.cpp_info.components["libtorch_c10"].includedirs.append(os.path.join("include", "torch", "csrc", "api", "include"))
        self.cpp_info.components["libtorch_c10"].requires.extend(["fmt::fmt", "onnx::onnx"])
        self.cpp_info.components["libtorch_c10"].requires.extend(
            _tbb() + _fbgemm() + _nnpack() + _xnnpack() + _pthreadpool() +
            _opencl()
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
            self.cpp_info.components["libtorch_c10d"].requires.extend(["_libtorch"] + _openmpi() + _gloo())

        # process_group_agent & tensorpipe_agent
        if self.options.get_safe("with_tensorpipe"):
            self.cpp_info.components["libtorch_process_group_agent"].libs = ["process_group_agent"]
            self.cpp_info.components["libtorch_process_group_agent"].requires.extend(["_libtorch", "libtorch_c10d"])
            self.cpp_info.components["libtorch_tensorpipe_agent"].libs = ["tensorpipe_agent"]
            self.cpp_info.components["libtorch_tensorpipe_agent"].requires.extend(["_libtorch", "libtorch_c10d", "fmt::fmt"] + _tensorpipe())

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

        # caffe2_rocksdb
        if self.options.with_rocksdb:
            self.cpp_info.components["libtorch_caffe2_rocksdb"].libs = ["caffe2_rocksdb"]
            self.cpp_info.components["libtorch_caffe2_rocksdb"].requires.extend(["_libtorch", "rocksdb::rocksdb"])

        if self.options.utilities:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
