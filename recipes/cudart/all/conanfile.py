from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks
from conan.tools.scm import Version
import os
from os.path import isdir, join, exists

required_conan_version = ">=1.47.0"

class CudaRtConan(ConanFile):
    name = "cudart"
    description = "NVIDIA CUDA Runtime"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("cuda", "nvidia", "runtime")
    settings = "os", "arch"
    options = {}
    default_options = {}
    no_copy_source = True

    def requirements(self):
        self.requires(f"nvcc/{self.version}")

    def package_info(self):
        nvcc = self.dependencies["nvcc"]
        components = ["cudadevrt", "cudart", "cudart_static"]
        self.cpp_info.set_property("cmake_file_name", "cudart")
        for component in components:
            name = component.lower()
            if component in nvcc.cpp_info.components:
                self.cpp_info.components[component].libdirs = []
                self.cpp_info.components[component].resdirs = []
                self.cpp_info.components[component].bindirs = []
                self.cpp_info.components[component].includedirs = []
                self.cpp_info.components[component].libs = []
                self.cpp_info.components[name].requires = [f"nvcc::{component}"]
            