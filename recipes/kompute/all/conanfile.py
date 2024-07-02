from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, replace_in_file

import os

class komputeRecipe(ConanFile):
    name = "kompute"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://kompute.cc"
    description = "The general purpose GPU compute framework for cross vendor graphics cards (AMD, Qualcomm, NVIDIA & friends)"
    topics = ("gpu", "compute", "vulkan", "opencl")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_python": [True, False],
        "with_spdlog": [True, False],
        "android_build": [True, False],
        "build_shaders": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_python": False,
        "with_spdlog": True,
        "android_build": False,
        "build_shaders": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("vulkan-loader/1.3.243.0")
        self.requires("vulkan-headers/1.3.243.0")
        self.requires("fmt/10.1.1")
        if self.options.with_spdlog:
            self.requires("spdlog/1.12.0")
        if self.options.build_python:
            self.requires("pybind11/2.10.4")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20.0 <4]")

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("vulkan-headers", "cmake_target_name", "Vulkan::Headers")
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["KOMPUTE_OPT_INSTALL"] = True
        tc.variables["KOMPUTE_OPT_BUILD_PYTHON"] = self.options.build_python
        tc.variables["KOMPUTE_OPT_USE_SPDLOG"] = self.options.with_spdlog
        tc.variables["KOMPUTE_OPT_ANDROID_BUILD"] = self.options.android_build
        tc.variables["KOMPUTE_OPT_USE_BUILT_IN_SPDLOG"] = False
        tc.variables["KOMPUTE_OPT_SPDLOG_ASYNC_MODE"] = True
        tc.variables["KOMPUTE_OPT_USE_BUILT_IN_FMT"] = False
        tc.variables["KOMPUTE_OPT_USE_BUILT_IN_GOOGLE_TEST"] = False
        tc.variables["KOMPUTE_OPT_USE_BUILT_IN_PYBIND11"] = False
        tc.variables["KOMPUTE_OPT_USE_BUILT_IN_VULKAN_HEADER"] = False
        tc.generate()

    def build(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "find_package(Vulkan REQUIRED)",
            "find_package(Vulkan REQUIRED)\n        find_package(VulkanHeaders REQUIRED)",
        )
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["kompute"]
