from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import download, copy, unzip, symlinks, rmdir, rm
from conan.tools.scm import Version
import os
from os.path import isdir, join, exists

required_conan_version = ">=1.47.0"

class CudaToolkitConan(ConanFile):
    name = "cuda-toolkit"
    description = "Nvidia CUDA SDK toolkit"
    url = "https://github.com/rymut/conan-center-index-cuda-sdk"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("nvcc", "cuda", "nvidia", "SDK")
    exports_sources = ["cudatoolkit_toolchain.cmake"]
    settings = "os", "arch"
    options = {
        "use_cccl": [True, False],
        "use_cudnn": [True, False],
        "cudnn_version": [None, "ANY"],
        "use_cudart": [True, False],
        "use_cuobjdump": [True, False],
        "use_cupti": [True, False],
        "use_cuxxfit": [True, False],
        "use_gdb": [True, False],
        "use_memcheck": [True, False],
        "use_nvcc": [True, False],
        "use_nvdisasm": [True, False],
        "use_nvprof": [True, False],
        "use_nvprune": [True, False],
        "use_nvrtc": [True, False],
        "use_nvtx": [True, False], # windows only
        "use_sanitizer_api": [True, False],
        # libraries
        "use_nvml": [True, False],
        "use_cudacxx": [True, False],
        "use_cub": [True, False],
        "use_thrust": [True, False],
        "use_cublas": [True, False],
        "use_cufft": [True, False],
        "use_curand": [True, False],
        "use_cusolver": [True, False],
        "use_cusparse": [True, False],
        "use_npp": [True, False],
        "use_nvjpeg": [True, False],
        # integration elements true for visual studio usage
        "use_visual_studio_integration": [True, False]
    }
    default_options = {
        "use_cccl": True,
        "use_cudnn": False,
        "cudnn_version": None,
        "use_cudart": True,
        "use_cuobjdump": True,
        "use_gdb": True,
        "use_cupti": True,
        "use_cuxxfit": True,
        "use_memcheck": True,
        "use_nvcc": True,
        "use_nvdisasm": True,
        "use_nvml": True,
        "use_nvprof": True,
        "use_nvprune": True,
        "use_nvrtc": True,
        "use_nvtx": True, # windows only
        "use_sanitizer_api": True,
        "use_cudacxx": True,
        "use_cub": True,
        "use_thrust": True,
        "use_cublas": True,
        "use_cufft": True,
        "use_curand": True,
        "use_cusolver": True,
        "use_cusparse": True,
        "use_npp": True,
        "use_nvjpeg": True,
        "use_visual_studio_integration": True
    }
    no_copy_source = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        if self.options.use_cccl:
            self.requires("thrust/1.17.2")

    def build_requirements(self):
        if getattr(self._settings_build, 'os') == "Windows":
            self.tool_requires("7zip/19.00")

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.use_gdb
        if self.settings.os != "Windows":
            del self.options.use_visual_studio_integration

    def validate(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only windows and linux os is supported")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only x86_64 is supported")
        if self.options.use_cudnn is True and self.options.cudnn_version == "None":
            raise ConanInvalidConfiguration("Setting cudnn_version must be set when cudnn is true")
        if self.options.use_cudnn is False and self.options.cudnn_version is not None:
            raise ConanInvalidConfiguration("Setting cudnn_version cannot be set when cudnn is false")
        if self.options.use_cudnn:
            if not os.path.exists(self._filepath_cudnn) or not os.path.isfile(self._filepath_cudnn):
                raise ConanInvalidConfiguration(f"Building with cudnn=True require setting CUDNN_PATH variable containing {self._filename_cudnn}")
        if self.options.use_cccl is True:
            if not self.options.use_thrust or not self.options.use_cub or not self.options.use_cudacxx:
                raise ConanInvalidConfiguration("cccl must enable thrust, cub, cudacxx")

    @property
    def _filename(self):
        filename = f"cuda_{self.version}.run"
        if self.settings.os == "Windows":
            filename = f"cuda_{self.version}.exe"
        return filename

    @property
    def _filename_cudnn(self):
        return f"cudnn_{self.options.cudnn_version}.zip"

    @property
    def _path_cudnn(self):
        return os.environ.get('CUDNN_PATH')

    @property
    def _filepath_cudnn(self):
        return join(self._path_cudnn, self._filename_cudnn)

    def build(self):
        if self.options.use_cudnn:
            unzip(self, self._path_cudnn, destination="cudnn", strip_root=True)
        src = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        download(self, **src, filename=self._filename)
        if "Windows" == str(self.settings.os):
            self.run(f"7z x {self._filename}")
        elif "Linux" == str(self.settings.os):
            self.run(f"./{self._filename} --extract={self.build_folder}")

    def _package_linux(self):
        targets = join("targets", f"{self.settings.arch}-linux")
        inc_dst = join(targets, "include")
        lib_dst = join(targets, "lib")
        copy(self, "version.*", self.build_folder, self.package_folder)
        copy(self, "EULA.txt", self.build_folder, join(self.package_folder, "licenses"))

        def install_basic(name):
            src = join(self.build_folder, name)
            dst = self.package_folder
            for dirname in ["bin", "src", "share", "targets"]:
                if isdir(join(src, dirname)):
                    copy(self, "*", join(src, dirname), join(dst, dirname))

        def install_custom(name, src_rel, dst_rel=None):
            if dst_rel is None:
                dst_rel = src_rel
            src = join(self.build_folder, name, src_rel)
            dst = join(self.package_folder, dst_rel)
            if exists(src):
                copy(self, "*", src, dst)

        if self.options.use_thrust:
            install_custom("cuda_cccl", f"{targets}/include/thrust")
            install_custom("cuda_cccl", f"{targets}/lib/cmake/thrust")
        if self.options.use_cub:
            install_custom("cuda_cccl", f"{targets}/include/cub")
            install_custom("cuda_cccl", f"{targets}/lib/cmake/cub")
        if self.options.use_cudacxx:
            install_custom("cuda_cccl", f"{targets}/include/cuda")
            install_custom("cuda_cccl", f"{targets}/lib/cmake/nv")
        if self.options.use_cudart:
            install_basic("cuda_cudart")
        if self.options.use_cuobjdump:
            install_basic("cuda_cuobjdump")
        if self.options.use_cupti:
            install_custom("cuda_cupti", "extras/CUPTI/include")
            install_custom("cuda_cupti", "extras/CUPTI/lib64")
        if self.options.use_cuxxfit:
            install_basic("cuda_cuxxfit")
        # skip cuda_demo_suite
        # skip cuda_documentation
        if self.options.use_gdb:
            install_basic("cuda_gdb")
            install_custom("cuda_gdb", "extras/Debugger")
        if self.options.use_memcheck:
            install_basic("cuda_memcheck")
        # skip nsight
        if self.options.use_nvcc:
            install_basic("cuda_nvcc")
            install_custom("cuda_nvcc", "nvvm/bin")
            install_custom("cuda_nvcc", "nvvm/include")
            install_custom("cuda_nvcc", "nvvm/lib64")
            install_custom("cuda_nvcc", "nvvm/libdevice")
        if self.options.use_nvdisasm:
            install_basic("cuda_nvdisasm")
        if self.options.use_nvml:
            install_basic("cuda_nvml_dev")
        if self.options.use_nvprof:
            install_basic("cuda_nvprof")
        if self.options.use_nvprune:
            install_basic("cuda_nvprune")
        if self.options.use_nvrtc:
            install_basic("cuda_nvrtc")
        if self.options.use_nvtx:
            install_basic("cuda_nvtx")
        # skip nvvp - nvidia visual profiler
        # skip cuda_samples
        if self.options.use_sanitizer_api:
            install_custom("cuda_sanatizer_api", "compute-sanatizer")
            rmdir(self, join(self.package_folder, "compute-sanatizer/docs"))
        # skip integration
        if self.options.use_cublas:
            install_basic("libcublas")
        if self.options.use_cufft:
            install_basic("libcufft")
        if self.options.use_curand:
            install_basic("libcurand")
        if self.options.use_cusolver:
            install_basic("libcusolver")
        if self.options.use_cusparse:
            install_basic("libcusparse")
        if self.options.use_npp:
            install_basic("libnvpp")
        if self.options.use_nvjpeg:
            install_basic("libnvjpeg")
        # skip nsight_compute
        # skip nsigth_systems
        if self.options.use_cudnn:
            copy(self, "LICENSE", join(self.build_folder, "cudnn"), join(self.package_folder, "licenses"))
            install_custom(join("cudnn", "include"),  join("nvcc", "include"))
            install_custom(join("cudnn", "lib"),  join("nvcc", "lib", "x64"))
            install_custom(join("cudnn", "bin"), join("nvcc", "bin"))
        os.symlink(join(self.package_folder, inc_dst), join(self.package_folder, "include"))
        os.symlink(join(self.package_folder, lib_dst), join(self.package_folder, "lib64"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    @property
    def _toolkit_dir(self):
        if self.settings.os == "Windows":
            return "nvcc"
        return "."

    @property
    def _lib_dir(self):
        if self.settings.os == "Windows":
            return "lib/x64"
        return "lib64"

    @property
    def _bin_dir(self):
        if self.settings.os == "Windows":
            return "bin"
        return "lib64"

    def _package_windows(self):
        def install_custom(name, src_rel, dst_rel=None):
            if dst_rel is None:
                dst_rel = src_rel
            src = join(self.build_folder, name, src_rel)
            dst = join(self.package_folder, dst_rel)
            if exists(src):
                copy(self, "*", src, dst)

        copy(self, "version.*", self.build_folder, join(self.package_folder, self._toolkit_dir))
        copy(self, "EULA.txt", join(self.build_folder, "cuda_documentation", "Doc"), join(self.package_folder, "licenses"))
        if exists(join(self.build_folder, "CUDAToolkit", "version.txt")):
            copy(self, "version.txt", join(self.build_folder, "CUDAToolkit"), join(self.package_folder, self._toolkit_dir))
        if exists(join(self.build_folder, "CUDAToolkit", "version.json")):
            copy(self, "version.json", join(self.build_folder, "CUDAToolkit"), join(self.package_folder, self._toolkit_dir))
        if self.options.use_cudart:
            install_custom("cuda_cudart", "cudart", self._toolkit_dir)
        if self.options.use_cuobjdump:
            install_custom("cuda_cuobjdump", "cuobjdump", self._toolkit_dir)
        if self.options.use_cupti:
            install_custom("cuda_cupti", "cupti", self._toolkit_dir)
        if self.options.use_cuxxfit:
            install_custom("cuda_cuxxfit", "cuxxfit", self._toolkit_dir)
        if self.options.use_memcheck:
            install_custom("cuda_memcheck", "memcheck", self._toolkit_dir)
        if self.options.use_nvcc:
            install_custom("cuda_nvcc", "nvcc", self._toolkit_dir)
        if self.options.use_nvdisasm:
            install_custom("cuda_nvdisasm", "nvdisasm", self._toolkit_dir)
        if self.options.use_nvml:
            install_custom("cuda_nvml_dev", "nvml_dev", self._toolkit_dir)
        if self.options.use_nvprof:
            install_custom("cuda_nvprof", "nvprof", self._toolkit_dir)
        if self.options.use_nvprune:
            install_custom("cuda_nvprune", "nvprune", self._toolkit_dir)
        if self.options.use_nvrtc:
            install_custom("cuda_nvrtc", "nvrtc", self._toolkit_dir)
            install_custom("cuda_nvrtc", "nvrtc_dev", self._toolkit_dir)
        if self.options.use_sanitizer_api:
            install_custom("cuda_sanitizer_api", "sanitizer", self._toolkit_dir)
        if self.options.use_cublas:
            install_custom("libcublas", "cublas", self._toolkit_dir)
            install_custom("libcublas", "cublas_dev", self._toolkit_dir)
        if self.options.use_thrust:
            install_custom("cuda_thrust", join("thrust"), self._toolkit_dir)
            install_custom("cuda_cccl", join("thrust", "include", "thrust"), join(self._toolkit_dir, "include/thrust"))
            install_custom("cuda_cccl", join("thrust", "lib", "cmake", "thrust"), join(self._toolkit_dir, "lib/cmake/thrust"))
        if self.options.use_cub:
            install_custom("cuda_cccl", join("thrust", "include", "cub"), join(self._toolkit_dir, "include/cub"))
            install_custom("cuda_cccl", join("thrust", "lib", "cmake", "cub"), join(self._toolkit_dir, "lib/cmake/cub"))
        if self.options.use_cudacxx:
            install_custom("cuda_cccl", join("thrust", "include", "cuda"), join(self._toolkit_dir, "include/cuda"))
            install_custom("cuda_cccl", join("thrust", "include", "nv"), join(self._toolkit_dir, "include/nv"))
        if self.settings.os == "Windows":
            if self.options.use_nvtx:
                install_custom("cuda_nvtx", "nvtx", self._toolkit_dir)
            if self.options.use_visual_studio_integration:
                install_custom("visual_studio_integration", ".", ".")
        if self.options.use_cufft:
            install_custom("libcufft", "cufft", self._toolkit_dir)
            install_custom("libcufft", "cufft_dev", self._toolkit_dir)
        if self.options.use_curand:
            install_custom("libcurand", "curand", self._toolkit_dir)
            install_custom("libcurand", "curand_dev", self._toolkit_dir)
        if self.options.use_cusolver:
            install_custom("libcusolver", "cusolver", self._toolkit_dir)
            install_custom("libcusolver", "cusolver_dev", self._toolkit_dir)
        if self.options.use_cusparse:
            install_custom("libcusparse", "cusparse", self._toolkit_dir)
            install_custom("libcusparse", "cusparse_dev", self._toolkit_dir)
        if self.options.use_npp:
            install_custom("libnpp", "npp", self._toolkit_dir)
            install_custom("libnpp", "npp_dev", self._toolkit_dir)
        if self.options.use_nvjpeg:
            install_custom("libnvjpeg", "nvjpeg", self._toolkit_dir)
            install_custom("libnvjpeg", "nvjpeg_dev", self._toolkit_dir)
        if self.options.use_cudnn:
            copy(self, "LICENSE", join(self.build_folder, "cudnn"), join(self.package_folder, "licenses"))
            install_custom("cudnn", "include",  join(self._toolkit_dir, "include"))
            install_custom("cudnn", "lib",  join(self._toolkit_dir, self._lib_dir))
            install_custom("cudnn", "bin", join(self._toolkit_dir, "bin"))
        rm(self, "*.nvi", join(self.package_folder), recursive=True)

    def package(self):
        copy(self, "cudatoolkit_toolchain.cmake", self.export_sources_folder, self.package_folder)
        if self.settings.os == "Linux":
            self._package_linux()
        elif self.settings.os == "Windows":
            self._package_windows()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CUDAToolkit")
        components = ["cudart", "cudart_static", "cuda_driver", "cublas", "cublas_static", "cufft", "cufftw",
                          "cufft_static", "cufftw_static", "curand", "curand_static", "cusolver", "cusolver_static",
                          "cusparse", "cusparse_static", "cupti", "cupti_static", "nppc", "nppc_static", "nppial",
                          "nppial_static", "nppicc", "nppicc_static", "nppicom", "nppicom_static", "nppidei",
                          "nppidei_static", "nppif", "nppif_static", "nppig", "nppig_static", "nppim", "nppim_static",
                          "nppist", "nppist_static", "nppisu", "nppisu_static", "nppitc", "nppitc_static", "npps",
                          "npps_static", "nvblas", "nvrtc", "nvml", "OpenCL", "culibos"]

        self_ver = Version(self.version)
        if self_ver >= Version("9.2.0"):
            components += ["cufft_static_nocallback"]
        if self_ver >= Version("10.0"):
            components += ["nvjpeg", "nvjpeg_static", "nvtx3"]
        if self_ver < Version("10.0"):
            components += ["nvToolsExt"]
        if self_ver >= Version("10.1"):
            components += ["cublasLt", "cublasLt_static"]
        if self_ver < Version("11.0"):
            components += ["nvgraph", "nvgraph_static"]
        if self_ver >= Version("11.4"):
            components += ["cuFile", "cuFile_static", "cuFile_rdma", "cuFile_rdma_static"]
        if self_ver >= Version("11.1"):
            components += ["nvptxcompiler"]

        for component in components:
            name = component.lower()
            self.cpp_info.components[name].set_property("cmake_target_name", "CUDA::" + component)
            self.cpp_info.components[name].libdirs = [self._lib_dir]
            self.cpp_info.components[name].resdirs = []
            self.cpp_info.components[name].bindirs = [self._bin_dir]
            self.cpp_info.components[name].includedirs = [join(self._toolkit_dir, 'include')]
            if exists(join(self.package_folder, self._lib_dir, f"lib{component}.so")) or exists(join(self.package_folder, self._lib_dir, f"lib{component}.a")):
                self.cpp_info.components[name].lib = [f"lib{component}"]
            elif exists(join(self.package_folder, self._lib_dir, f"{component}.lib")):
                self.cpp_info.components[name].lib = [f"{component}.lib"]

        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "cudatoolkit_toolchain.cmake"))
        if self.settings.os == "Windows":
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, self._toolkit_dir, "bin", "nvcc.exe") })
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_arch", f"x64,cuda={self.package_folder.replace(os.sep, '/')}")
            self.buildenv_info.define("CUDAToolkit_ROOT", self.package_folder)
            self.buildenv_info.define("CUDA_PATH", self.package_folder)
            self.runenv_info.define("CUDA_PATH", self.package_folder)
        else:
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc") })
            self.buildenv_info.define("CUDAToolkit_ROOT", self.package_folder)
            self.runenv_info.append_path("LD_LIBRARY_PATH", join(self.package_folder, self._bin_dir))
