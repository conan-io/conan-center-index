from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.53.0"


class VolkConan(ConanFile):
    name = "volk"
    license = "MIT"
    homepage = "https://github.com/zeux/volk"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "volk is a meta-loader for Vulkan. It allows you to dynamically load "
        "entrypoints required to use Vulkan without linking to vulkan-1.dll or "
        "statically linking Vulkan loader. Additionally, volk simplifies the "
        "use of Vulkan extensions by automatically loading all associated "
        "entrypoints. Finally, volk enables loading Vulkan entrypoints "
        "directly from the driver which can increase performance by skipping "
        "loader dispatch overhead."
    )
    topics = ("vulkan", "loader", "extension", "entrypoint", "graphics")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_x11": True,
        "with_wayland": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        elif self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11
            del self.options.with_wayland

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)
        if self.options.get_safe("with_x11"):
            # volk.h:176 <xcb/xcb.h>
            self.requires("xorg/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    @property
    def _platform_defines(self):
        if self.settings.os == "Windows":
            return ["VK_USE_PLATFORM_WIN32_KHR"]
        elif self.settings.os == "Android":
            return ["VK_USE_PLATFORM_ANDROID_KHR"]
        elif is_apple_os(self):
            return ["VK_USE_PLATFORM_METAL_EXT"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            defines = []
            if self.options.with_x11:
                defines.extend(["VK_USE_PLATFORM_XCB_KHR", "VK_USE_PLATFORM_XLIB_KHR"])
            if self.options.with_wayland:
                defines.append("VK_USE_PLATFORM_WAYLAND_KHR")
            return defines
        return []

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VOLK_PULL_IN_VULKAN"] = True
        tc.variables["VOLK_INSTALL"] = True        
        if self._platform_defines:
            tc.cache_variables["VOLK_STATIC_DEFINES"] = ";".join(self._platform_defines)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(
            self,
            cmakelists,
            "if(VULKAN_HEADERS_INSTALL_DIR)",
            "if(1)\nfind_package(VulkanHeaders REQUIRED)\nset(VOLK_INCLUDES ${VulkanHeaders_INCLUDE_DIRS})\nelseif(VULKAN_HEADERS_INSTALL_DIR)",
        )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "volk")

        self.cpp_info.components["libvolk"].set_property("cmake_target_name", "volk::volk")
        self.cpp_info.components["libvolk"].libs = ["volk"]
        self.cpp_info.components["libvolk"].defines = self._platform_defines
        self.cpp_info.components["libvolk"].requires = ["vulkan-headers::vulkan-headers"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libvolk"].system_libs = ["dl"]
            if self.options.with_x11:
                self.cpp_info.components["libvolk"].requires.append("xorg::xcb")

        self.cpp_info.components["volk_headers"].set_property("cmake_target_name", "volk::volk_headers")
        self.cpp_info.components["volk_headers"].libs = []
        self.cpp_info.components["volk_headers"].defines = self._platform_defines
        self.cpp_info.components["volk_headers"].requires = ["vulkan-headers::vulkan-headers"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["volk_headers"].system_libs = ["dl"]
            if self.options.with_x11:
                self.cpp_info.components["volk_headers"].requires.append("xorg::xcb")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["libvolk"].names["cmake_find_package"] = "volk"
        self.cpp_info.components["libvolk"].names["cmake_find_package_multi"] = "volk"
