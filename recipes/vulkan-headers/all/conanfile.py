import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2"


class VulkanHeadersConan(ConanFile):
    name = "vulkan-headers"
    description = "Vulkan Header files."
    license = "Apache-2.0"
    topics = ("vulkan-headers", "vulkan")
    homepage = "https://github.com/KhronosGroup/Vulkan-Headers"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    package_id_embed_mode = "patch_mode"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["VULKAN_HEADERS_ENABLE_MODULE"] = False
        tc.cache_variables["VULKAN_HEADERS_ENABLE_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "*", src=os.path.join(self.package_folder, "share", "vulkan", "registry"), dst=os.path.join(self.package_folder, "res", "vulkan", "registry"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VulkanHeaders")
        self.cpp_info.components["vulkanheaders"].set_property("cmake_target_name", "Vulkan::Headers")
        self.cpp_info.components["vulkanheaders"].bindirs = []
        self.cpp_info.components["vulkanheaders"].libdirs = []

        self.cpp_info.components["vulkanregistry"].set_property("cmake_target_name", "Vulkan::Registry")
        self.cpp_info.components["vulkanregistry"].includedirs = [os.path.join("res", "vulkan", "registry")]
        self.cpp_info.components["vulkanregistry"].bindirs = []
        self.cpp_info.components["vulkanregistry"].libdirs = []
        self.cpp_info.components["vulkanregistry"].resdirs = ["res"]
