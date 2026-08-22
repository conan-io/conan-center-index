import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class SpirvReflectConan(ConanFile):
    name = "spirv-reflect"
    homepage = "https://github.com/KhronosGroup/SPIRV-Reflect"
    description = ("SPIRV-Reflect is a lightweight library that provides a C/C++ reflection API "
                   "for SPIR-V shader bytecode in Vulkan applications.")
    license = "Apache-2.0"
    topics = ("spirv", "spirv-v", "vulkan", "opengl", "opencl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"spirv-headers/{self.version}", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPIRV_REFLECT_STATIC_LIB"] = True
        tc.variables["SPIRV_REFLECT_EXAMPLES"] = False
        tc.variables["SPIRV_REFLECT_BUILD_TESTS"] = False
        tc.generate()

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "spirv-reflect-static")
        self.cpp_info.set_property("cmake_target_name", "spirv-reflect-static")
        self.cpp_info.libs = ["spirv-reflect-static"]
        self.cpp_info.defines.append("SPIRV_REFLECT_USE_SYSTEM_SPIRV_H")
