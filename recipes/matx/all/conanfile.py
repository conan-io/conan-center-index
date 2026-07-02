from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=2.30"


class MatxConan(ConanFile):
    name = "matx"
    description = (
        "MatX is a modern C++ library for numerical computing on NVIDIA GPUs and CPUs. "
        "Near-native performance can be achieved while using a simple syntax common in higher-level languages such as Python or MATLAB."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/MatX"
    topics = ("hpc", "gpu", "cuda", "gpgpu", "gpu-computing")
    package_type = "header-library"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD", "Windows"):
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}.")
        # matx/1.0.0 needs cuda-toolkit >=13.x as it depends on CCCL > 3.3.0
        # This recipe is not calling CPM
        min_cppstd = 17 if Version(self.version) < "1.0.0" else 20
        check_min_cppstd(self, min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "lib"))
        # Upstream creates this file with rapids_cmake_write_version_file(include/version_config.h)
        # As we are not using cmake.install(), we have to create it by our own
        matx_version = Version(self.version)
        save(
            self,
            os.path.join(self.package_folder, "include/matx/version_config.h"),
            textwrap.dedent(f"""
                #pragma once
                #define MATX_VERSION_MAJOR {matx_version.major}
                #define MATX_VERSION_MINOR {matx_version.minor}
                #define MATX_VERSION_PATCH {matx_version.patch}
            """),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Upstream: https://github.com/NVIDIA/MatX/blob/v1.0.0/CMakeLists.txt#L135-L136
        self.cpp_info.includedirs.append(os.path.join("include", "matx", "kernels"))
        self.cpp_info.set_property("cmake_extra_dependencies", ["CUDAToolkit"])
        self.cpp_info.set_property(
            "cmake_extra_interface_libs",
            [
                "CUDA::cublas",
                "CUDA::cublasLt",
                "CUDA::cuda_driver",
                "CUDA::cudart",
                "CUDA::cufft",
                "CUDA::curand",
                "CUDA::cusolver",
                "CUDA::cusparse",
            ],
        )
