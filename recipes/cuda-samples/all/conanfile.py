import os

from conan import ConanFile
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class CudaSamplesConan(ConanFile):
    name = "cuda-samples"
    description = ("Common headers from NVIDIA CUDA Samples - "
                   "samples for CUDA developers which demonstrate features in CUDA Toolkit")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/cuda-samples"
    topics = ("cuda", "cuda-kernels", "cuda-driver-api", "cuda-opengl", "nvcudasamples")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Package only headers under Common/ folder
        rmdir(self, os.path.join(self.source_folder, "Samples"))
        rmdir(self, os.path.join(self.source_folder, "bin"))
        # Skip GL headers and precompiled libs, since these should be provided by separate Conan packages
        rmdir(self, os.path.join(self.source_folder, "Common", "GL"))
        rmdir(self, os.path.join(self.source_folder, "Common", "lib"))
        rmdir(self, os.path.join(self.source_folder, "Common", "data"))

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include", "Common"),
             src=os.path.join(self.source_folder, "Common"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs.append(os.path.join("include", "Common"))
