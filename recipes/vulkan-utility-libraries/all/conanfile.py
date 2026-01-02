from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
import os

required_conan_version = ">=2.1.0"


class VulkanUtilityLibrariesConan(ConanFile):
    name = "vulkan-utility-libraries"
    description = "The Vulkan-ValidationLayers contained many libraries and utilities that were useful for other Vulkan repositories."
    license = "Apache-2.0"
    topics = ("vulkan-utility-libraries", "vulkan")
    homepage = "https://github.com/KhronosGroup/Vulkan-Utility-Libraries"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PACKAGE_BUILD_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

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

        self.cpp_info.components["UtilityHeaders"].libs = []
        self.cpp_info.components["UtilityHeaders"].includedirs = ["include"]
        self.cpp_info.components["UtilityHeaders"].set_property("cmake_target_name", "Vulkan::UtilityHeaders")
        self.cpp_info.components["UtilityHeaders"].requires = ["vulkan-headers::vulkan-headers"]

        self.cpp_info.components["SafeStruct"].libs = ["VulkanSafeStruct"]
        self.cpp_info.components["SafeStruct"].set_property("cmake_target_name", "Vulkan::SafeStruct")
        self.cpp_info.components["SafeStruct"].requires = ["UtilityHeaders", "vulkan-headers::vulkan-headers"]

        self.cpp_info.components["LayerSettings"].libs = ["VulkanLayerSettings"]
        self.cpp_info.components["LayerSettings"].set_property("cmake_target_name", "Vulkan::LayerSettings")
        self.cpp_info.components["LayerSettings"].requires = ["UtilityHeaders", "vulkan-headers::vulkan-headers"]
