from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2"


class D3D12MemoryAllocatorConan(ConanFile):
    name = "d3d12-memory-allocator"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/D3D12MemoryAllocator"
    license = "MIT"
    description = "The open source memory allocation library for the D3D12 API"
    topics = ("allocator", "directx", "direct3d", "gpu", "graphics")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only available in Windows")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["D3D12MA_BUILD_SAMPLE"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "D3D12MemoryAllocator")
        self.cpp_info.set_property("cmake_target_name", "GPUOpen::D3D12MemoryAllocator")
        postfix = {"Release": "", "Debug": "d", "RelWithDebInfo": "rd", "MinSizeRel": "s"}[str(self.settings.build_type)]
        self.cpp_info.libs = [f"D3D12MA{postfix}"]
