from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class VulkanValidationLayersConan(ConanFile):
    name = "vulkan-validationlayers"
    description = "Khronos official Vulkan validation layers for Windows, Linux, Android, and MacOS."
    license = "Apache-2.0"
    topics = ("conan", "vulkan-validation-layers", "vulkan", "validation-layers")
    homepage = "https://github.com/KhronosGroup/Vulkan-ValidationLayers"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_wsi_xcb": [True, False],
        "with_wsi_xlib": [True, False],
        "with_wsi_wayland": [True, False]
    }
    default_options = {
        "with_wsi_xcb": True,
        "with_wsi_xlib": True,
        "with_wsi_wayland": True
    }

    short_paths = True

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 is not supported")

    def requirements(self):
        self.requires("glslang/8.13.3559")
        self.requires("spirv-tools/v2020.5")
        self.requires("vulkan-headers/{}".format(self.version))
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.18.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("Vulkan-ValidationLayers-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "add_compile_options(-Werror)", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'add_compile_options("/WX")', "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'add_compile_options("/GR-")', "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "FindVulkanHeaders.cmake"),
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/share/vulkan/registry",
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/res/vulkan/registry")
        tools.replace_in_file(os.path.join(self._source_subfolder, "layers", "CMakeLists.txt"),
                              "install(FILES ${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>/${TARGET_NAME}.json DESTINATION ${CMAKE_INSTALL_LIBDIR})",
                              "install(FILES ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${TARGET_NAME}.json DESTINATION ${CMAKE_INSTALL_LIBDIR})")
        tools.replace_in_file(os.path.join(self._source_subfolder, "layers", "CMakeLists.txt"),
                              "install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${TARGET_NAME}.json DESTINATION ${CMAKE_INSTALL_LIBDIR})",
                              "install(FILES ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${TARGET_NAME}.json DESTINATION ${CMAKE_INSTALL_LIBDIR})")

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
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["INSTALL_TESTS"] = False
        self._cmake.definitions["BUILD_LAYERS"] = True
        self._cmake.definitions["BUILD_LAYER_SUPPORT_FILES"] = False
        self._cmake.configure()
        return self._cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os != "Windows":
            os.rename(os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        if not tools.is_apple_os(self.settings.os):
            self.cpp_info.libs = ["VkLayer_utils"]

        manifest_subfolder = "lib" if self.settings.os == "Windows" else os.path.join("res", "vulkan", "explicit_layer.d")
        vk_layer_path = os.path.join(self.package_folder, manifest_subfolder)
        self.output.info("Appending VK_LAYER_PATH environment variable: {}".format(vk_layer_path))
        self.env_info.VK_LAYER_PATH.append(vk_layer_path)
