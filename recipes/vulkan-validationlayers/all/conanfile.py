from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class VulkanValidationLayersConan(ConanFile):
    name = "vulkan-validationlayers"
    description = "Khronos official Vulkan validation layers for Windows, Linux, Android, and MacOS."
    license = "Apache-2.0"
    topics = ("vulkan", "validation-layers")
    homepage = "https://github.com/KhronosGroup/Vulkan-ValidationLayers"
    url = "https://github.com/conan-io/conan-center-index"

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

    short_paths = True

    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland

    @property
    def _get_compatible_spirv_tools_version(self):
        return {
            "1.2.189.2": "2021.3",
            "1.2.182": "2021.2",
            "1.2.154.0": "2020.5",
        }.get(str(self.version), False)

    @property
    def _get_compatible_vulkan_headers_version(self):
        return {
            "1.2.189.2": "1.2.189",
            "1.2.182": "1.2.182",
            "1.2.154.0": "1.2.154.0",
        }.get(str(self.version), False)

    @staticmethod
    def _greater_equal_semver(v1, v2):
        lv1 = [int(v) for v in v1.split(".")]
        lv2 = [int(v) for v in v2.split(".")]
        diff_len = len(lv2) - len(lv1)
        if diff_len > 0:
            lv1.extend([0] * diff_len)
        elif diff_len < 0:
            lv2.extend([0] * -diff_len)
        return lv1 >= lv2

    def requirements(self):
        # TODO: set private=True, once the issue is resolved https://github.com/conan-io/conan/issues/9390
        self.requires("spirv-tools/{}".format(self._get_compatible_spirv_tools_version), private=not hasattr(self, "settings_build"))
        self.requires("vulkan-headers/{}".format(self._get_compatible_vulkan_headers_version))
        # TODO: use tools.Version comparison once https://github.com/conan-io/conan/issues/10000 is fixed
        if self._greater_equal_semver(self.version, "1.2.173"):
            self.requires("robin-hood-hashing/3.11.3")
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.19.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        if self.options["spirv-tools"].shared:
            raise ConanInvalidConfiguration("vulkan-validationlayers can't depend on shared spirv-tools")

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 is not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "FindVulkanHeaders.cmake"),
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/share/vulkan/registry",
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/res/vulkan/registry")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["VULKAN_HEADERS_INSTALL_DIR"] = self.deps_cpp_info["vulkan-headers"].rootpath
        self._cmake.definitions["USE_CCACHE"] = False
        if self.settings.os == "Linux":
            self._cmake.definitions["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
            self._cmake.definitions["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
            self._cmake.definitions["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
        self._cmake.definitions["BUILD_WERROR"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["INSTALL_TESTS"] = False
        self._cmake.definitions["BUILD_LAYERS"] = True
        self._cmake.definitions["BUILD_LAYER_SUPPORT_FILES"] = True
        self._cmake.configure()
        return self._cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Windows":
            # import lib is useless, validation layers are loaded at runtime
            lib_dir = os.path.join(self.package_folder, "lib")
            tools.remove_files_by_mask(lib_dir, "VkLayer_khronos_validation.lib")
            tools.remove_files_by_mask(lib_dir, "libVkLayer_khronos_validation.dll.a")
        else:
            # Move json files to res, but keep in mind to preserve relative
            # path between module library and manifest json file
            os.rename(os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.libs = ["VkLayer_utils"]

        manifest_subfolder = "bin" if self.settings.os == "Windows" else os.path.join("res", "vulkan", "explicit_layer.d")
        vk_layer_path = os.path.join(self.package_folder, manifest_subfolder)
        self.output.info("Appending VK_LAYER_PATH environment variable: {}".format(vk_layer_path))
        self.env_info.VK_LAYER_PATH.append(vk_layer_path)
