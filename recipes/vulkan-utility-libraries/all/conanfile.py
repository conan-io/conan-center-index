import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class VulkanUtilityLibrariesConan(ConanFile):
    name = "vulkan-utility-libraries"
    homepage = "https://github.com/KhronosGroup/Vulkan-Utility-Libraries/tree/main"
    description = "Utility libraries for Vulkan developers"
    license = "Apache-2.0"
    topics = ("vulkan-utility-libraries", "vulkan", "gpu")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
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
        self.cpp_info.set_property("cmake_file_name", "VulkanUtilityLibraries")
        self.cpp_info.set_property("cmake_target_name", "Vulkan::UtilityLibraries")
        self.cpp_info.libs = ["VulkanLayerSettings", "VulkanSafeStruct"]
