from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, replace_in_file
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
        "with_dxheaders": [True, False],
    }
    default_options = {
        "shared": False,
        "with_dxheaders": False,
    }

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only available in Windows")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def requirements(self):
        if self.options.with_dxheaders:
            self.requires("directx-headers/[>=1.618.2 <2]", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["D3D12MA_BUILD_SAMPLE"] = False

        if self.options.with_dxheaders:
            tc.preprocessor_definitions["D3D12MA_USING_DIRECTX_HEADERS"] = "1"

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if self.options.with_dxheaders:
            cmakelists_path = os.path.join(self.source_folder, "src/CMakeLists.txt")

            replace_in_file(self, cmakelists_path,
                            "add_library(D3D12MemoryAllocator",
                            "find_package(DirectX-Headers REQUIRED)\nadd_library(D3D12MemoryAllocator")
            replace_in_file(self, cmakelists_path,
                            "target_link_libraries(D3D12MemoryAllocator",
                            "target_link_libraries(D3D12MemoryAllocator PUBLIC Microsoft::DirectX-Headers)\ntarget_link_libraries(D3D12MemoryAllocator")


        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.options.with_dxheaders:
            self.cpp_info.defines.append("D3D12MA_USING_DIRECTX_HEADERS")
            self.cpp_info.requires = ["directx-headers::directx-headers"]

        self.cpp_info.set_property("cmake_file_name", "D3D12MemoryAllocator")
        self.cpp_info.set_property("cmake_target_name", "GPUOpen::D3D12MemoryAllocator")
        postfix = {"Release": "", "Debug": "d", "RelWithDebInfo": "rd", "MinSizeRel": "s"}[str(self.settings.build_type)]
        self.cpp_info.libs = [f"D3D12MA{postfix}"]
