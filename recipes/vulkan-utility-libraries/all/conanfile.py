from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class VulkanUtilityLibrariesConan(ConanFile):
    name = "vulkan-utility-libraries"
    description = "Utility libraries for Vulkan developers."
    license = "Apache-2.0"
    topics = ("vulkan", "utility-libraries")
    homepage = "https://github.com/KhronosGroup/Vulkan-Utility-Libraries"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    package_id_embed_mode = "patch_mode"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("vulkan-headers/1.4.328.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.set_property("cmake_file_name", "VulkanUtilityLibraries")
        self.cpp_info.set_property("cmake_target_name", "Vulkan::UtilityLibraries")