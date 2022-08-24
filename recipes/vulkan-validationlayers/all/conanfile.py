from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException, ConanInvalidConfiguration
import functools
import glob
import os
import shutil
import yaml

required_conan_version = ">=1.35.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _dependencies_filename(self):
        return f"dependencies-{self.version}.yml"

    @property
    @functools.lru_cache(1)
    def _dependencies_versions(self):
        dependencies_filepath = os.path.join(self.recipe_folder, "dependencies", self._dependencies_filename)
        if not os.path.isfile(dependencies_filepath):
            raise ConanException(f"Cannot find {dependencies_filepath}")
        cached_dependencies = yaml.safe_load(open(dependencies_filepath))
        return cached_dependencies

    def export(self):
        self.copy(self._dependencies_filename, src="dependencies", dst="dependencies")

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland

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
        self.requires(self._require("spirv-tools"), private=not hasattr(self, "settings_build"))
        self.requires(self._require("vulkan-headers"))
        # TODO: use tools.Version comparison once https://github.com/conan-io/conan/issues/10000 is fixed
        if self._greater_equal_semver(self.version, "1.2.173"):
            self.requires("robin-hood-hashing/3.11.5")
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.20.0")

    def _require(self, recipe_name):
        if recipe_name not in self._dependencies_versions:
            raise ConanException(f"{recipe_name} is missing in {self._dependencies_filename}")
        return f"{recipe_name}/{self._dependencies_versions[recipe_name]}"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

        if self.options["spirv-tools"].shared:
            raise ConanInvalidConfiguration("vulkan-validationlayers can't depend on shared spirv-tools")

        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 is not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "FindVulkanHeaders.cmake"),
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/share/vulkan/registry",
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/res/vulkan/registry")
        # FIXME: two CMake module/config files should be generated (SPIRV-ToolsConfig.cmake and SPIRV-Tools-optConfig.cmake),
        # but it can't be modeled right now in spirv-tools recipe
        if not os.path.exists("SPIRV-Tools-optConfig.cmake"):
            shutil.copy("SPIRV-ToolsConfig.cmake", "SPIRV-Tools-optConfig.cmake")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["VULKAN_HEADERS_INSTALL_DIR"] = self.deps_cpp_info["vulkan-headers"].rootpath
        cmake.definitions["USE_CCACHE"] = False
        if self.settings.os in ["Linux", "FreeBSD"]:
            cmake.definitions["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
            cmake.definitions["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
            cmake.definitions["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
        cmake.definitions["BUILD_WERROR"] = False
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["INSTALL_TESTS"] = False
        cmake.definitions["BUILD_LAYERS"] = True
        cmake.definitions["BUILD_LAYER_SUPPORT_FILES"] = True
        cmake.configure()
        return cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Windows":
            # import lib is useless, validation layers are loaded at runtime
            lib_dir = os.path.join(self.package_folder, "lib")
            tools.files.rm(self, lib_dir, "VkLayer_khronos_validation.lib")
            tools.files.rm(self, lib_dir, "libVkLayer_khronos_validation.dll.a")
            # move dll and json manifest files in bin folder
            bin_dir = os.path.join(self.package_folder, "bin")
            tools.files.mkdir(self, bin_dir)
            for ext in ("*.dll", "*.json"):
                for bin_file in glob.glob(os.path.join(lib_dir, ext)):
                    shutil.move(bin_file, os.path.join(bin_dir, os.path.basename(bin_file)))
        else:
            # Move json files to res, but keep in mind to preserve relative
            # path between module library and manifest json file
            tools.files.rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.libs = ["VkLayer_utils"]

        manifest_subfolder = "bin" if self.settings.os == "Windows" else os.path.join("res", "vulkan", "explicit_layer.d")
        vk_layer_path = os.path.join(self.package_folder, manifest_subfolder)
        self.output.info("Prepending to VK_LAYER_PATH runtime environment variable: {}".format(vk_layer_path))
        self.runenv_info.prepend_path("VK_LAYER_PATH", vk_layer_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.VK_LAYER_PATH.append(vk_layer_path)
