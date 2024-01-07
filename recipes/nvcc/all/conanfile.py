from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks, patch, export_conandata_patches, rm, rmdir, rename
from conan.tools.scm import Version
import os
from os import chmod
from os.path import isdir, join, exists

required_conan_version = ">=1.47.0"

# TODO
# - [ ] nvcc.profile patch for windows & linux
# - [ ] MSbuild Platform patch for  windows
# - [ ] Put DLL files in bin path (windows)
# - [ ] Create cudart "depends" - library that requires nvcc package
# - [ ] Create nvrtc "depends" - library that requires nvcc package
class NvccConan(ConanFile):
    name = "nvcc"
    description = "NVIDIA CUDA Compiler Driver NVCC"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("nvcc", "compiler", "cuda", "nvidia", "SDK")
    exports_sources = ["nvcc_toolchain.cmake"]
    package_type = "application"
    settings = "os", "arch"
    options = {}
    default_options = {}
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
        if exists(join(nvvm_root, "lib64")):
            rename(self, join(nvvm_root, "lib64"), join(nvvm_root, "lib"))
        if exists(join(nvvm_root, "nvvm-samples")):
            rmdir(self, join(self, nvvm_root, "nvvm-samples"))
        # patching
        for it in self.conan_data.get("patches", {}).get(str(self.version), []):
            if str(self.settings.os).lower() in it.get("patch_file", ""):
                patch(self, **it, base_path=self.build_folder)

    def package(self):
        copy(self, "nvcc_toolchain.cmake", self.export_sources_folder, self.package_folder)
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        dirs = ["bin", "lib", "include", "nvvm"]
        for name in dirs:
            if exists(join(self.build_folder, name)):
                copy(self, "*", join(self.build_folder, name), join(self.package_folder, name))
        if exists(join(self.build_folder, "visual_studio_integration")):
            copy(self, "*", join(self.build_folder, "visual_studio_integration"), join(self.package_folder, "CUDAVisualStudioIntegration", "extras", "visual_studio_integration"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)

    @property
    def _is_windows(self):
        return str(self.settings.os) == "Windows"

    def package_info(self):
        # nvcc libraries
        if self.version >= Version("11.1"):
            self.cpp_info.components["nvptxcompiler_static"].set_property("cmake_target_aliases", ["CUDA::nvptxcompiler_static"])
            self.cpp_info.components["nvptxcompiler_static"].libs = ["nvptxcompiler_static"]

        # nvvm libraries
        self.cpp_info.components["nvvm"].includedirs = ["nvvm/include"]
        self.cpp_info.components["nvvm"].libdirs = ["nvvm/lib"]
        self.cpp_info.components["nvvm"].bindirs = ["nvvm/bin"] if self._is_windows else ["nvvm/bin", "nvvm/lib"]
        self.cpp_info.components["nvvm"].libs = ["nvvm"]

        # cudart libraries
        self.cpp_info.components["cudart"].set_property("cmake_target_aliases", ["CUDA::cudart"])
        self.cpp_info.components["cudart"].libs = ["cudart"]

        self.cpp_info.components["cudart_static"].set_property("cmake_target_aliases", ["CUDA::cudart_static"])
        self.cpp_info.components["cudart_static"].libs = ["cudart_static"]

        self.cpp_info.components["cuda"].set_property("cmake_target_aliases", ["CUDA::cuda_driver"])
        self.cpp_info.components["cuda"].libs = ["cuda"]

        self.cpp_info.components["cudadevrt"].set_property("cmake_target_aliases", ["CUDA::cudadevrt"])
        self.cpp_info.components["cudadevrt"].libs = ["cudadevrt"]

        # toolchain
        run_extension = ".exe" if self._is_windows else ""
        self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc" + run_extension) })
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "nvcc_toolchain.cmake"))
        if self._is_windows:
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_arch", f"x64,cuda={self.package_folder.replace(os.sep, '/')}")
