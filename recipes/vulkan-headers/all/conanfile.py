from conans import ConanFile, tools
import os

required_conan_version = ">=1.36.0"


class VulkanHeadersConan(ConanFile):
    name = "vulkan-headers"
    description = "Vulkan Header files."
    license = "Apache-2.0"
    topics = ("vulkan-headers", "vulkan")
    homepage = "https://github.com/KhronosGroup/Vulkan-Headers"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self.source_folder, self._source_subfolder, "include"))
        self.copy("*", dst=os.path.join("res", "vulkan", "registry"),
                       src=os.path.join(self.source_folder, self._source_subfolder, "registry"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VulkanHeaders")
        self.cpp_info.set_property("cmake_target_name", "Vulkan")
        self.cpp_info.components["vulkanheaders"].set_property("cmake_target_name", "Headers")
        self.cpp_info.components["vulkanheaders"].bindirs = []
        self.cpp_info.components["vulkanheaders"].libdirs = []
        self.cpp_info.components["vulkanregistry"].set_property("cmake_target_name", "Registry")
        self.cpp_info.components["vulkanregistry"].includedirs = [os.path.join("res", "vulkan", "registry")]
        self.cpp_info.components["vulkanregistry"].bindirs = []
        self.cpp_info.components["vulkanregistry"].libdirs = []
