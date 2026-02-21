from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, cmake_layout
import os


class SDL3WebGPU(ConanFile):
    name = "sdl3webgpu"
    description = "An extension for the SDL3 library for using WebGPU native"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eliemichel/sdl3webgpu"
    topics = ("sdl3", "graphics", "wgsl", "emscripten")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "CMakeLists.txt"
    generators = "CMakeToolchain", "CMakeConfigDeps"

    options = {
        "emdawnwebgpu": [True, False],
    }
    default_options = {
        "emdawnwebgpu": False,
    }

    def requirements(self):
        self.requires("sdl/[>3]")

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination="./subdir",
            strip_root=True
        )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            pattern="sdl3webgpu.h",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.libs = ["sdl3webgpu"]
        self.cpp_info.set_property("cmake_file_name", "SDL3WebGPU")
        self.cpp_info.set_property("cmake_target_name", "SDL3WebGPU::SDL3WebGPU")
        if self.options.emdawnwebgpu:
            self.cpp_info.defines = ["WEBGPU_BACKEND_EMDAWNWEBGPU=1"]
