from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class VulkanHeadersConan(ConanFile):
    name = "vulkan-headers"
    description = "Vulkan Header files."
    license = "Apache-2.0"
    topics = ("vulkan-headers", "vulkan")
    homepage = "https://github.com/KhronosGroup/Vulkan-Headers"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", src=os.path.join(self.source_folder, "registry"), dst=os.path.join(self.package_folder, "res", "vulkan", "registry"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VulkanHeaders")
        self.cpp_info.components["vulkanheaders"].set_property("cmake_target_name", "Vulkan::Headers")
        self.cpp_info.components["vulkanheaders"].bindirs = []
        self.cpp_info.components["vulkanheaders"].frameworkdirs = []
        self.cpp_info.components["vulkanheaders"].libdirs = []
        self.cpp_info.components["vulkanregistry"].set_property("cmake_target_name", "Vulkan::Registry")
        self.cpp_info.components["vulkanregistry"].includedirs = [os.path.join("res", "vulkan", "registry")]
        self.cpp_info.components["vulkanregistry"].bindirs = []
        self.cpp_info.components["vulkanregistry"].frameworkdirs = []
        self.cpp_info.components["vulkanregistry"].libdirs = []

        self.cpp_info.filenames["cmake_find_package"] = "VulkanHeaders"
        self.cpp_info.filenames["cmake_find_package_multi"] = "VulkanHeaders"
        self.cpp_info.names["cmake_find_package"] = "Vulkan"
        self.cpp_info.names["cmake_find_package_multi"] = "Vulkan"
        self.cpp_info.components["vulkanheaders"].names["cmake_find_package"] = "Headers"
        self.cpp_info.components["vulkanheaders"].names["cmake_find_package_multi"] = "Headers"
        self.cpp_info.components["vulkanregistry"].names["cmake_find_package"] = "Registry"
        self.cpp_info.components["vulkanregistry"].names["cmake_find_package_multi"] = "Registry"
