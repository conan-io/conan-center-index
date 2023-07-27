from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy

import os.path

class DXCRecipe(ConanFile):
    name = "dxc"
    license = "NCSA"
    author = "Copyright (c) Microsoft Corporation. Copyright (c) 2003-2015 University of Illinois at Urbana-Champaign."
    url = "https://github.com/microsoft/DirectXShaderCompiler"
    description = "DirectX Shader Compiler which is based on LLVM/Clang."
    topics = ("dxc", "hlsl", "dxil", "shader-programs", "directx-shader-compiler")

    settings = "os", "arch"
    options = {}
    default_options = {}

    def validate(self):
        if str(self.settings.os) not in ("Windows", "Linux"):
            raise ConanInvalidConfiguration("DXC only works on Windows and Linux!")

    def build(self):
        get(self, **self.conan_data["source"][self.version][str(self.settings.os)][0])

    def package(self):
        arch = str(self.settings.arch).lower()
        if arch == "x86_64":
            arch = "x64"

        if self.settings.os == "Windows":
            copy(self, "*", os.path.join(self.build_folder, "inc"), os.path.join(self.package_folder, "include"))
            copy(self, "*", os.path.join(self.build_folder, f"lib/{arch}"), os.path.join(self.package_folder, "lib"))
            copy(self, "*", os.path.join(self.build_folder, f"bin/{arch}"), os.path.join(self.package_folder, "bin"))
        else:
            copy(self, "*", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"))
            copy(self, "*", os.path.join(self.build_folder, "lib"), os.path.join(self.package_folder, "lib"))
            copy(self, "*", os.path.join(self.build_folder, "bin"), os.path.join(self.package_folder, "bin"))

        copy(self, "LICENSE-*", self.build_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["dxcompiler"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]

        if self.settings.os == "Window":
            self.cpp_info.defines = ["__DXC_TEST_WINDOWS"]
