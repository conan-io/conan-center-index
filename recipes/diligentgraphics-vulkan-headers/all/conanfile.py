import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class VulkanHeadersConan(ConanFile):
    name = "diligentgraphics-vulkan-headers"
    description = "Diligent fork of Vulkan Header files."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/Vulkan-Headers"
    topics = ("vulkan-headers", "vulkan", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    provides = "vulkan-headers"
    deprecated = "vulkan-headers"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "*",
             dst=os.path.join("res", "vulkan", "registry"),
             src=os.path.join(self.source_folder, "registry"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "VulkanHeaders")
        self.cpp_info.set_property("cmake_target_name", "Vulkan::Vulkan")

        self.cpp_info.components["vulkanheaders"].set_property("cmake_target_name", "Vulkan::Headers")
        self.cpp_info.components["vulkanheaders"].bindirs = []
        self.cpp_info.components["vulkanheaders"].libdirs = []
        self.cpp_info.components["vulkanregistry"].set_property("cmake_target_name", "Vulkan::Registry")
        self.cpp_info.components["vulkanregistry"].includedirs = [os.path.join("res", "vulkan", "registry")]
        self.cpp_info.components["vulkanregistry"].bindirs = []
        self.cpp_info.components["vulkanregistry"].libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "VulkanHeaders"
        self.cpp_info.filenames["cmake_find_package_multi"] = "VulkanHeaders"
        self.cpp_info.names["cmake_find_package"] = "Vulkan"
        self.cpp_info.names["cmake_find_package_multi"] = "Vulkan"

        self.cpp_info.components["vulkanheaders"].names["cmake_find_package"] = "Headers"
        self.cpp_info.components["vulkanheaders"].names["cmake_find_package_multi"] = "Headers"
        self.cpp_info.components["vulkanregistry"].names["cmake_find_package"] = "Registry"
        self.cpp_info.components["vulkanregistry"].names["cmake_find_package_multi"] = "Registry"
