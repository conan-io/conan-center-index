from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, save, copy, symlinks
from conan.tools.scm import Version
import os
from os.path import isdir, join, exists

required_conan_version = ">=1.47.0"

class NvccConan(ConanFile):
    name = "nvcc"
    description = "NVIDIA CUDA Compiler Driver NVCC"
    url = "https://github.com/rymut/conan-center-index"
    homepage = "https://developer.nvidia.com/cuda-downloads"
    license = "Nvidia CUDA Toolkit EULA"
    topics = ("nvcc", "compiler", "cuda", "nvidia", "SDK")
    exports_sources = ["nvcc_toolchain.cmake"]
    settings = "os", "arch"
    provides = ["cudart", "nvrtc"]
    options = {}
    default_options = {}
    no_copy_source = True

    def validate(self):
        if not self.settings.os in ["Windows", "Linux"]:
            raise ConanInvalidConfiguration("Only windows and linux os is supported")
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only x86_64 is supported")

    def build(self):
        srcs = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        if isinstance(srcs, list):
            for src in srcs:
                get(self, **src, strip_root=True)
        else:
            get(self, **srcs, strip_root=True)

    def package(self):
        def install_custom(name, src_rel, dst_rel=None):
            if dst_rel is None:
                dst_rel = src_rel
            src = join(self.build_folder, name, src_rel)
            dst = join(self.package_folder, dst_rel)
            if exists(src):
                copy(self, "*", src, dst)

        copy(self, "LICENSE", self.build_folder, join(self.package_folder, "licenses"))
        dirs = ["bin", "lib", "lib64", "include", "nvvm"]
        for name in dirs:
            if exists(join(self.build_folder, name)):
                copy(self, "*", join(self.build_folder, name), join(self.package_folder, name))
        if exists(join(self.build_folder, "visual_studio_integration")):
            copy(self, "*", join(self.build_folder, "visual_studio_integration"), join(self.package_folder, "CUDAVisualStudioIntegration", "extras", "visual_studio_integration"))
        symlinks.absolute_to_relative_symlinks(self, self.package_folder)


    def package_info(self):
        def bin_dir():
            if self.settings.os == "Windows":
                return "bin"
            return "lib64"

        def lib_dir():
            if self.settings.os == "Windows":
                return "lib/x64"
            return "lib64"

        def lib_name(name):
            if exists(join(self.package_folder, lib_dir(), f"lib{name}.so")) or exists(join(self.package_folder, lib_dir(), f"lib{name}.a")):
                return [f"lib{name}"]
            elif exists(join(self.package_folder, lib_dir(), f"{name}.lib")):
                return [f"{name}.lib"]
            elif exists(join(self.package_folder, "lib", f"{name}.lib")):
                return [f"{name}.lib"]
            return []

        self.cpp_info.set_property("cmake_file_name", "nvcc")
        self.cpp_info.components["nvvm"].set_property("cmake_target_name", "nvvm")
        self.cpp_info.components["nvvm"].libdirs = [f"nvvm/{lib_dir()}"]
        self.cpp_info.components["nvvm"].resdirs = []
        self.cpp_info.components["nvvm"].bindirs = [f"nvvm/{bin_dir()}"]
        self.cpp_info.components["nvvm"].includedirs = ["nvvm/include"]
        self.cpp_info.components["nvvm"].lib = lib_name("nvvm")

        if self.version >= Version("11.1"):
            self.cpp_info.components["nvptxcompiler_static"].set_property("cmake_target_name", "nvptxcompiler_static")
            self.cpp_info.components["nvptxcompiler_static"].libdirs = ["lib"]
            self.cpp_info.components["nvptxcompiler_static"].resdirs = []
            self.cpp_info.components["nvptxcompiler_static"].bindirs = ["bin"]
            self.cpp_info.components["nvptxcompiler_static"].includedirs = ["include"]
            self.cpp_info.components["nvptxcompiler_static"].lib = lib_name("nvptxcompiler_static")

        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", join(self.package_folder, "nvcc_toolchain.cmake"))
        if self.settings.os == "Windows":
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc.exe") })
            self.conf_info.define("tools.cmake.cmaketoolchain:toolset_arch", f"x64,cuda={self.package_folder.replace(os.sep, '/')}")
        else:
            self.conf_info.update("tools.build:compiler_executables", { "cuda": join(self.package_folder, "bin", "nvcc") })
