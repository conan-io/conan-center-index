import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class VulkanExtensionLayerConan(ConanFile):
    name = "vulkan-extensionlayer"
    homepage = "https://github.com/KhronosGroup/Vulkan-ExtensionLayer"
    description = "Layer providing Vulkan features when native support is unavailable"
    license = "Apache-2.0"
    topics = ("vulkan-extensionlayer", "vulkan", "gpu")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-utility-libraries/{self.version}", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VulkanExtensionLayer")
        self.cpp_info.set_property("cmake_target_name", "Vulkan::ExtensionLayer")
        self.cpp_info.libs = ["VulkanLayerSettings", "VulkanSafeStruct"]
