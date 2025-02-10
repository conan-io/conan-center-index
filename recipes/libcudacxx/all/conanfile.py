import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, move_folder_contents, export_conandata_patches, apply_conandata_patches, rename
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class LibcudacxxConan(ConanFile):
    name = "libcudacxx"
    description = ("libcu++, the NVIDIA C++ Standard Library, is the C++ Standard Library for your entire system."
                   " It provides a heterogeneous implementation of the C++ Standard Library that can be used in and between CPU and GPU code.")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nvidia.github.io/libcudacxx/"
    topics = ("cuda", "standard-library", "libcxx", "gpu", "nvidia", "nvidia-hpc-sdk", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        move_folder_contents(self, os.path.join(self.source_folder, "libcudacxx"), self.source_folder)
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE.TXT",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "libcudacxx-config.cmake",
             src=os.path.join(self.source_folder, "lib", "cmake", "libcudacxx"),
             dst=os.path.join(self.package_folder, "lib", "cmake"))
        rename(self, os.path.join(self.package_folder, "lib", "cmake", "libcudacxx-config.cmake"),
                     os.path.join(self.package_folder, "lib", "cmake", "libcudacxx-config-official.cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # Follows the naming conventions of the official CMake config file:
        # https://github.com/NVIDIA/cccl/blob/main/libcudacxx/lib/cmake/libcudacxx/libcudacxx-config.cmake
        self.cpp_info.set_property("cmake_file_name", "libcudacxx")
        # Disable the target. It is created in the .cmake module instead.
        self.cpp_info.set_property("cmake_target_name", "_libcudacxx_do_not_use")

        # The CMake module ensures that the include dir is exported as a non-SYSTEM include in CMake
        # https://github.com/NVIDIA/cccl/blob/v2.2.0/libcudacxx/lib/cmake/libcudacxx/libcudacxx-config.cmake#L11-L29
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        module_path = os.path.join("lib", "cmake", "libcudacxx-config-official.cmake")
        self.cpp_info.set_property("cmake_build_modules", [module_path])
