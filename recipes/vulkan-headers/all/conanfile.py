from conans import ConanFile, tools
import glob
import os


class VulkanHeadersConan(ConanFile):
    name = "vulkan-headers"
    description = "Vulkan Header files."
    license = "Apache-2.0"
    topics = ("conan", "vulkan-headers", "vulkan")
    homepage = "https://github.com/KhronosGroup/Vulkan-Headers"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("Vulkan-Headers-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self.source_folder, self._source_subfolder, "include"))
        self.copy("*", dst=os.path.join("res", "vulkan", "registry"),
                       src=os.path.join(self.source_folder, self._source_subfolder, "registry"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "VulkanHeaders"
        self.cpp_info.filenames["cmake_find_package_multi"] = "VulkanHeaders"
        self.cpp_info.names["cmake_find_package"] = "Vulkan"
        self.cpp_info.names["cmake_find_package_multi"] = "Vulkan"
        self.cpp_info.components["vulkanheaders"].names["cmake_find_package"] = "Headers"
        self.cpp_info.components["vulkanheaders"].names["cmake_find_package_multi"] = "Headers"
        self.cpp_info.components["vulkanheaders"].bindirs = []
        self.cpp_info.components["vulkanheaders"].libdirs = []
        self.cpp_info.components["vulkanregistry"].names["cmake_find_package"] = "Registry"
        self.cpp_info.components["vulkanregistry"].names["cmake_find_package_multi"] = "Registry"
        self.cpp_info.components["vulkanregistry"].includedirs = [os.path.join("res", "vulkan", "registry")]
        self.cpp_info.components["vulkanregistry"].bindirs = []
        self.cpp_info.components["vulkanregistry"].libdirs = []
