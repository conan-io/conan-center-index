from conan import ConanFile
from conan.tools.files import get, copy, load, save
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        cmakelists_path = os.path.join(self.source_folder, "CMakeLists.txt")
        cmakelists_content = load(self, cmakelists_path)
        save(self, cmakelists_path, "cmake_minimum_required(VERSION 3.10)\n"+cmakelists_content)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

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
