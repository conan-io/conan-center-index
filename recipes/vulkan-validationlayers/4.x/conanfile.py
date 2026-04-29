from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rename, rm
from conan.tools.gnu import PkgConfigDeps
import os

required_conan_version = ">=2.1"


class VulkanValidationLayersConan(ConanFile):
    name = "vulkan-validationlayers"
    description = "Khronos official Vulkan validation layers for Windows, Linux, Android, and MacOS."
    license = "Apache-2.0"
    topics = ("vulkan", "validation-layers")
    homepage = "https://github.com/KhronosGroup/Vulkan-ValidationLayers"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_wsi_xcb": [True, False],
        "with_wsi_xlib": [True, False],
        "with_wsi_wayland": [True, False],
    }
    default_options = {
        "with_wsi_xcb": True,
        "with_wsi_xlib": True,
        "with_wsi_wayland": True,
    }

    implements = ["auto_shared_fpic"]

    @property
    def _has_wsi_options(self):
        return self.settings.os not in ["Windows", "Android"] and not is_apple_os(self)

    @property
    def _needs_pkg_config(self):
        return self.options.get_safe("with_wsi_xcb") or \
               self.options.get_safe("with_wsi_xlib") or \
               self.options.get_safe("with_wsi_wayland")

    def config_options(self):
        if not self._has_wsi_options:
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("robin-hood-hashing/3.11.5")
        self.requires("spirv-headers/1.4.341.0")
        self.requires("spirv-tools/1.4.341.0")
        self.requires("vulkan-headers/1.4.341.0", transitive_headers=True)
        self.requires("vulkan-utility-libraries/1.4.341.0")

        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.22.0")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration("vulkan-validationlayers can't depend on shared spirv-tools")

    def build_requirements(self):
        if self._needs_pkg_config and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.1 <3]")
        self.tool_requires("cmake/[>=3.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["VVL_CLANG_TIDY"] = False
        tc.cache_variables["USE_CCACHE"] = False
        if self._has_wsi_options:
            tc.cache_variables["BUILD_WSI_XCB_SUPPORT"] = self.options.get_safe("with_wsi_xcb")
            tc.cache_variables["BUILD_WSI_XLIB_SUPPORT"] = self.options.get_safe("with_wsi_xlib")
            tc.cache_variables["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.get_safe("with_wsi_wayland")
        tc.cache_variables["BUILD_WERROR"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["INSTALL_TESTS"] = False
        tc.cache_variables["BUILD_LAYERS"] = True
        tc.cache_variables["BUILD_LAYER_SUPPORT_FILES"] = True
        tc.generate()

        deps = CMakeDeps(self)
        # Conan provides both under the same name, upstream only uses this one
        deps.set_property("spirv-tools", "cmake_file_name", "SPIRV-Tools-opt")
        deps.generate()

        if self._needs_pkg_config:
            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        if not self.settings.os == "Windows":
            # Move json files to res, but keep in mind to preserve relative
            # path between module library and manifest json file
            rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        manifest_subfolder = "bin" if self.settings.os == "Windows" else os.path.join("res", "vulkan", "explicit_layer.d")
        vk_layer_path = os.path.join(self.package_folder, manifest_subfolder)
        self.runenv_info.prepend_path("VK_LAYER_PATH", vk_layer_path)

        if self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["android", "log"])
