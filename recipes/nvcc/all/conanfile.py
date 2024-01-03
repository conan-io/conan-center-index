from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks, patch, export_conandata_patches, rm
from conan.tools.scm import Version
import os
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
        if isinstance(srcs, list):
            for src in srcs:
                get(self, **src, strip_root=True)
        else:
            get(self, **srcs, strip_root=True)
        copy(self, "*.dll", join(self.build_folder, "lib"), join(self.build_folder, "bin"))
        rm(self, "*.dll", join(self.build_folder, "lib"))
        for it in self.conan_data.get("patches", {}).get(str(self.version), []):
            if str(self.settings.os).lower() in it.get("patch_file", ""):
                patch(self, **it, base_path=self.build_folder)

    def package(self):
        copy(self, "nvcc_toolchain.cmake", self.export_sources_folder, self.package_folder)
        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        dirs = ["bin", "lib", "lib64", "include", "nvvm"]
        for name in dirs:
            if exists(join(self.build_folder, name)):
                copy(self, "*", join(self.build_folder, name), join(self.package_folder, name))
        if exists(join(self.build_folder, "visual_studio_integration")):
            copy(self, "*", join(self.build_folder, "visual_studio_integration"), join(self.package_folder, "CUDAVisualStudioIntegration", "extras", "visual_studio_integration"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)


    def package_info(self):
        def lib(name):
            libdirs = ["lib", "lib64", "lib/x64", "nvvm/lib", "nvvm/lib64", "nvvm/lib/x64"]
            libnames = [f"lib{name}.a", f"lib{name}.so", f"{name}.lib"]
            for libdir in libdirs:
                for libname in libnames:
                    if exists(join(self.package_folder, libdir, libname)):
                        incdir = "include"
                        if libdir.startswith("nvvm"):
                            incdir = "nvvm/include"
                        return [libdir, incdir, name]
            return [None, None, None]
        
        def bin_dir():
            if self.settings.os == "Windows":
                if exists(join(self.package_folder, "bin")):
                    return ["bin"]
                return []
            if exists(join(self.package_folder, "lib")):
                return ["lib"]
            if exists(join(self.package_folder, "lib64")):
                return ["lib64"]
            return []
        components = ["cuda_driver",
            "cudadevrt", "cudart", "cudart_static",
            "nvrtc", "nvrtc_static", "nvrtc_builtins", "nvrtc_buildins_static",
            "nvptxcompiler_static",
            "OpenCL"]
        libraries = {
            "cuda_device": "cuda"
        }
        libraryToTargetName = {"cuda": "cuda_driver"}
        for component in components:
            libdir, incdir, libname = lib(libraries.get(component, component))
            if libname is None:
                continue
            self.cpp_info.components[component].set_property("cmake_target_aliases", [f"CUDA::{component}"])
            self.cpp_info.components[component].libdirs = [libdir]
            self.cpp_info.components[component].resdirs = []
            self.cpp_info.components[component].bindirs = bin_dir()
            self.cpp_info.components[component].includedirs = [incdir]
            self.cpp_info.components[component].libs = [libname]

        if bin_dir():
            self.runenv_info.prepend_path("PATH", join(self.package_folder, bin_dir()[0]))
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "nvcc_toolchain.cmake"))
        if self.settings.os == "Windows":
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc.exe") })
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_arch", f"x64,cuda={self.package_folder.replace(os.sep, '/')}")
        else:
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc") })
