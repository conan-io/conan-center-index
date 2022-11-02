from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rm
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import functools
import glob
import os
import shutil
import yaml

required_conan_version = ">=1.52.0"


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

    @property
    def _needs_wayland_for_build(self):
        return self.options.get_safe("with_wsi_wayland") and Version(self.version) < "1.3.231"

    @property
    def _needs_pkg_config(self):
        return self.options.get_safe("with_wsi_xcb") or \
               self.options.get_safe("with_wsi_xlib") or \
               self._needs_wayland_for_build

    def export(self):
        copy(self, f"dependencies/{self._dependencies_filename}", self.recipe_folder, self.export_folder)

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TODO: set private=True, once the issue is resolved https://github.com/conan-io/conan/issues/9390
        self.requires(self._require("spirv-tools"), private=not hasattr(self, "settings_build"))
        self.requires(self._require("vulkan-headers"))
        # TODO: use Version comparison once https://github.com/conan-io/conan/issues/10000 is fixed
        if Version(self.version) >= "1.2.173":
            self.requires("robin-hood-hashing/3.11.5")
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self._needs_wayland_for_build:
            self.requires("wayland/1.21.0")

    def _require(self, recipe_name):
        if recipe_name not in self._dependencies_versions:
            raise ConanException(f"{recipe_name} is missing in {self._dependencies_filename}")
        return f"{recipe_name}/{self._dependencies_versions[recipe_name]}"

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration("vulkan-validationlayers can't depend on shared spirv-tools")

        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 is not supported")

    def build_requirements(self):
        if self._needs_pkg_config and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.variables["VULKAN_HEADERS_INSTALL_DIR"] = self.dependencies["vulkan-headers"].package_folder.replace("\\", "/")
        tc.variables["USE_CCACHE"] = False
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.variables["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
            tc.variables["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
            tc.variables["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
        tc.variables["BUILD_WERROR"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["INSTALL_TESTS"] = False
        tc.variables["BUILD_LAYERS"] = True
        tc.variables["BUILD_LAYER_SUPPORT_FILES"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if self._needs_pkg_config:
            deps = PkgConfigDeps(self)
            deps.generate()
            # TODO: to remove when properly handled by conan (see https://github.com/conan-io/conan/issues/11962)
            env = Environment()
            env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
            env.vars(self).save_script("conanbuildenv_pkg_config_path")

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Unusual but prefer custom FindVulkanHeaders.cmake from upstream instead of config file of conan
        replace_in_file(self, cmakelists,
                              "find_package(VulkanHeaders REQUIRED)",
                              "find_package(VulkanHeaders REQUIRED MODULE)")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "FindVulkanHeaders.cmake"),
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/share/vulkan/registry",
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/res/vulkan/registry")
        # Ensure to use upstream FindWayland.cmake
        if self._needs_wayland_for_build:
            replace_in_file(self, cmakelists,
                                  "find_package(Wayland REQUIRED)",
                                  "find_package(Wayland REQUIRED MODULE)")
        # Useless and may fail
        if Version(self.version) >= "1.3.231":
            replace_in_file(self, cmakelists, "include(VVLGenerateSourceCode)", "")
        # FIXME: two CMake module/config files should be generated (SPIRV-ToolsConfig.cmake and SPIRV-Tools-optConfig.cmake),
        # but it can't be modeled right now in spirv-tools recipe
        if not os.path.exists(os.path.join(self.generators_folder, "SPIRV-Tools-optConfig.cmake")):
            shutil.copy(
                os.path.join(self.generators_folder, "SPIRV-ToolsConfig.cmake"),
                os.path.join(self.generators_folder, "SPIRV-Tools-optConfig.cmake"),
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == "Windows":
            # import lib is useless, validation layers are loaded at runtime
            lib_dir = os.path.join(self.package_folder, "lib")
            rm(self, "VkLayer_khronos_validation.lib", lib_dir)
            rm(self, "libVkLayer_khronos_validation.dll.a", lib_dir)
            # move dll and json manifest files in bin folder
            bin_dir = os.path.join(self.package_folder, "bin")
            mkdir(self, bin_dir)
            for ext in ("*.dll", "*.json"):
                for bin_file in glob.glob(os.path.join(lib_dir, ext)):
                    shutil.move(bin_file, os.path.join(bin_dir, os.path.basename(bin_file)))
        else:
            # Move json files to res, but keep in mind to preserve relative
            # path between module library and manifest json file
            rename(self, os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.libs = ["VkLayer_utils"]

        manifest_subfolder = "bin" if self.settings.os == "Windows" else os.path.join("res", "vulkan", "explicit_layer.d")
        vk_layer_path = os.path.join(self.package_folder, manifest_subfolder)
        self.output.info(f"Prepending to VK_LAYER_PATH runtime environment variable: {vk_layer_path}")
        self.runenv_info.prepend_path("VK_LAYER_PATH", vk_layer_path)
        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.VK_LAYER_PATH.append(vk_layer_path)
