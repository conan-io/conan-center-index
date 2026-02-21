from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
import os


class SDL3WebGPU(ConanFile):
    name = "sdl3webgpu"
    description = "An extension for the SDL3 library for using WebGPU native"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eliemichel/sdl3webgpu"
    topics = ("sdl3", "graphics", "wgsl", "emscripten")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        copy(self, pattern="sdl3webgpu.h", src=self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.components["sdl3"].libs =  "sdl3webgpu"
        self.cpp_info.set_property("cmake_file_name", "SDL3WebGPU")
        self.cpp_info.set_property("cmake_target_name", "SDL3WebGPU::SDL3WebGPU")

