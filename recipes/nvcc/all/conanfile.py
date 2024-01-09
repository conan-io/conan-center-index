from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks, patch, export_conandata_patches, rm, rmdir, rename, replace_in_file
from conan.tools.scm import Version
import os
from os import chmod
from os.path import isdir, join, exists
from re import match

required_conan_version = ">=1.47.0"

class NvccConan(ConanFile):
    name = "nvcc"
    description = "NVIDIA CUDA Compiler Driver NVCC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("nvcc", "compiler", "cuda", "nvidia")
    exports_sources = ["nvcc_toolchain.cmake"]
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def validate(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only windows and linux os is supported")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only x86_64 is supported")

    def export_sources(self):
        export_conandata_patches(self)

    def build(self):
        srcs = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        license_path = join(self.build_folder, "LICENSE")
        for src in srcs:
            get(self, **src, strip_root=True)
            if exists(license_path):
                chmod(license_path, 0o666)
        # nvcc package
        nvvm_root = join(self.build_folder, "nvvm")
        if exists(join(nvvm_root, "lib", "x64")):
            copy(self, "*", join(nvvm_root, "lib", "x64"), join(nvvm_root, "lib"))
            rmdir(self, join(nvvm_root, "lib", "x64"))
        if exists(join(nvvm_root, "lib64")):
            rename(self, join(nvvm_root, "lib64"), join(nvvm_root, "lib"))
        if exists(join(nvvm_root, "nvvm-samples")):
            rmdir(self, join(self, nvvm_root, "nvvm-samples"))
        if self._is_windows:
            copy(self, "*.dll", join(self.build_folder, "lib"), join(self.build_folder, "bin"))
            rm(self, "*.dll", join(self.build_folder, "lib"))
        # patching
        nvcc_profile_path = join(self.build_folder, "bin", "nvcc.profile")
        if self._is_windows:
            replace_in_file(self, nvcc_profile_path, "$(_WIN_PLATFORM_)", "")
            major, minor = match(r"(\d+)\.(\d+)", self.version).groups()
            props_path = join(self.build_folder, "visual_studio_integration", "MSBuildExtensions", f"CUDA {major}.{minor}.props")
            replace_in_file(self, props_path,
                r'''<CudaToolkitDir Condition="'$(CudaToolkitDir)' == ''">$(CudaToolkitCustomDir)</CudaToolkitDir>''',
                r'''<CudaToolkitDir Condition="'$(CudaToolkitDir)' == '' AND !Exists($(CudaToolkitCustomDir))">$([System.Text.RegularExpressions.Regex]::Replace( $(CudaToolkitCustomDir), '(nvcc[\\\/]?)$', '' ) )</CudaToolkitDir>'''
                r'''<CudaToolkitDir Condition="'$(CudaToolkitDir)' == ''">$(CudaToolkitCustomDir)</CudaToolkitDir>'''
                r'''<CudaToolkitDir Condition="'$(CudaToolkitDir)' != ''">$([System.Text.RegularExpressions.Regex]::Replace( $(CudaToolkitDir), '(res[\\\/]?)$', '' ) )</CudaToolkitDir>''')
            replace_in_file(self, props_path,
                r'''<CudaToolkitLibDir Condition="'$(CudaToolkitLibDir)' == ''">$(CudaToolkitDir)lib64</CudaToolkitLibDir>''',
                r'''<CudaToolkitLibDir Condition="'$(CudaToolkitLibDir)' == '' AND Exists('$(CudaToolkitDir)lib64')">$(CudaToolkitDir)lib64</CudaToolkitLibDir>'''
                r'''<CudaToolkitLibDir Condition="'$(CudaToolkitLibDir)' == ''">$(CudaToolkitDir)lib</CudaToolkitLibDir>''')
        else:
            replace_in_file(self, nvcc_profile_path, "$(_TARGET_SIZE_)", "")

    def package(self):
        copy(self, "nvcc_toolchain.cmake", self.export_sources_folder, join(self.package_folder, "res"))
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        copy(self, "*cu*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        copy(self, "*nv*", join(self.build_folder, "lib"), join(self.package_folder, "lib"))
        copy(self, "*", join(self.build_folder, "nvvm", "lib"), join(self.package_folder, "lib"))
        copy(self, "*", join(self.build_folder, "nvvm", "libdevice"), join(self.package_folder, "lib"))
        dirs = ["bin", "include"]
        for name in dirs:
            if exists(join(self.build_folder, name)):
                copy(self, "*", join(self.build_folder, name), join(self.package_folder, name))
                copy(self, "*", join(self.build_folder, "nvvm", name), join(self.package_folder, name))
        if exists(join(self.build_folder, "visual_studio_integration")):
            copy(self, "*", join(self.build_folder, "visual_studio_integration"), join(self.package_folder, "res", "CUDAVisualStudioIntegration", "extras", "visual_studio_integration"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    @property
    def _is_windows(self):
        return str(self.settings.os) == "Windows"

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        self.cpp_info.components["global"].builddirs = ["res"]
        self.cpp_info.components["global"].bindirs = ["bin"] if self._is_windows else ["bin", "lib"]
        # nvvm libraries
        self.cpp_info.components["nvvm"].includedirs = ["include"]
        self.cpp_info.components["nvvm"].libdirs = ["lib"]
        self.cpp_info.components["nvvm"].bindirs = ["bin"] if self._is_windows else ["bin", "lib"]
        self.cpp_info.components["nvvm"].libs = ["nvvm"]
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["nvvm"].system_libs = ["dl", "m"]

        # cudart libraries
        self.cpp_info.components["cudart"].set_property("cmake_target_aliases", ["CUDA::cudart"])
        self.cpp_info.components["cudart"].libs = ["cudart"]
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["cudart"].system_libs = ["dl"]

        self.cpp_info.components["cudart_static_deps"].set_property("cmake_target_aliases", ["CUDA::cudart_static_deps"])
        self.cpp_info.components["cudart_static_deps"].libdirs = []
        self.cpp_info.components["cudart_static_deps"].bindirs = []
        self.cpp_info.components["cudart_static_deps"].libs = []

        # unix system_libs
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["cudart_static_deps"].system_libs = ["pthread", "rt"]
        self.cpp_info.components["cudart_static"].set_property("cmake_target_aliases", ["CUDA::cudart_static"])
        self.cpp_info.components["cudart_static"].libs = ["cudart_static"]
        self.cpp_info.components["cudart_static"].requires = ["cudart_static_deps"]

        self.cpp_info.components["cuda_driver"].set_property("cmake_target_aliases", ["CUDA::cuda_driver", "CUDA::cuda"])
        if not self._is_windows:
            self.cpp_info.components["cuda_driver"].libdirs = ["lib/stubs"]
        self.cpp_info.components["cuda_driver"].libs = ["cuda"]

        self.cpp_info.components["cudadevrt"].set_property("cmake_target_aliases", ["CUDA::cudadevrt"])
        self.cpp_info.components["cudadevrt"].libs = ["cudadevrt"]

        if not self._is_windows:
            self.cpp_info.components["culibos"].set_property("cmake_target_aliases", ["CUDA::culibos"])
            self.cpp_info.components["culibos"].libs = ["culibos"]

        # nvcc libraries
        if self.version >= Version("11.1"):
            self.cpp_info.components["nvptxcompiler_static"].set_property("cmake_target_aliases", ["CUDA::nvptxcompiler_static"])
            self.cpp_info.components["nvptxcompiler_static"].libs = ["nvptxcompiler_static"]
            self.cpp_info.components["nvptxcompiler_static"].requires = ["cudart_static_deps"]

        # toolchain
        run_extension = ".exe" if self._is_windows else ""
        self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc" + run_extension) })
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "res", "nvcc_toolchain.cmake"))
        if self._is_windows:
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_arch", f"x64,cuda={join(self.package_folder, 'res').replace(os.sep, '/')}")
