from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks
from conan.tools.scm import Version
import os
from os.path import isdir, join, exists

required_conan_version = ">=1.47.0"

class CudaCompilerConan(ConanFile):
    name = "cuda-compiler"
    description = "NVIDIA CUDA compiler"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("cuda", "nvidia", "compiler")
    settings = "os", "arch"
    options = {}
    default_options = {}
    no_copy_source = True

    def requirements(self):
        self.requires(f"nvcc/{self.version}", build=False, run=True, visible=True)
        self.requires(f"cudart/{self.version}", libs=True, build=False, run=True, visible=True)


    def package_info(self):
        nvcc_root = self.dependencies['nvcc'].package_folder        
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(nvcc_root, "nvcc_toolchain.cmake"))
        if self.settings.os == "Windows":
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(nvcc_root, "bin", "nvcc.exe") })
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_arch", f"x64,cuda={nvcc_root.replace(os.sep, '/')}")
            self.runenv_info.prepend_path("PATH", join(self.package_folder, "bin"))
        else:
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(nvcc_root, "bin", "nvcc") })
            self.runenv_info.prepend_path("PATH", join(self.package_folder, "lib"))
