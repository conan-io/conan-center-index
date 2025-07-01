from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rm
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import glob
import os
import shutil


required_conan_version = ">=1.55.0"


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
        "fPIC": [True, False],
        "with_wsi_xcb": [True, False],
        "with_wsi_xlib": [True, False],
        "with_wsi_wayland": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_wsi_xcb": True,
        "with_wsi_xlib": True,
        "with_wsi_wayland": True,
    }

    short_paths = True

    @property
    def _needs_wayland_for_build(self):
        return (self.options.get_safe("with_wsi_wayland") and
                (Version(self.version) < "1.3.231" or Version(self.version) >= "1.3.243.0"))

    @property
    def _needs_pkg_config(self):
        return self.options.get_safe("with_wsi_xcb") or \
               self.options.get_safe("with_wsi_xlib") or \
               self._needs_wayland_for_build

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "1.3.235":
            return "17"
        return "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "apple-clang": "9",
                "clang": "6",
                "gcc": "7",
                "msvc": "191",
                "Visual Studio": "15.7",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "1.4.313.0":
            self.requires("parallel-hashmap/2.0.0")
        else:
            self.requires("robin-hood-hashing/3.11.5")

        if Version(self.version) >= "1.3.268.0":
            self.requires(f"vulkan-utility-libraries/{self.version}")

        self.requires(f"spirv-headers/{self.version}")
        self.requires(f"spirv-tools/{self.version}")
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self._needs_wayland_for_build:
            self.requires("wayland/1.22.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration("vulkan-validationlayers can't depend on shared spirv-tools")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 is not supported")

    def build_requirements(self):
        if self._needs_pkg_config and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
        if Version(self.version) >= "1.3.239":
            self.tool_requires("cmake/[>=3.17.2 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        if Version(self.version) >= "1.3.239":
            tc.cache_variables["VVL_CLANG_TIDY"] = False
        if Version(self.version) < "1.3.234":
            tc.variables["VULKAN_HEADERS_INSTALL_DIR"] = self.dependencies["vulkan-headers"].package_folder.replace("\\", "/")
        tc.variables["USE_CCACHE"] = False
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.variables["BUILD_WSI_XCB_SUPPORT"] = self.options.get_safe("with_wsi_xcb")
            tc.variables["BUILD_WSI_XLIB_SUPPORT"] = self.options.get_safe("with_wsi_xlib")
            tc.variables["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.get_safe("with_wsi_wayland")
        elif self.settings.os == "Android":
            tc.variables["BUILD_WSI_XCB_SUPPORT"] = False
            tc.variables["BUILD_WSI_XLIB_SUPPORT"] = False
            tc.variables["BUILD_WSI_WAYLAND_SUPPORT"] = False
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

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Vulkan-ValidationLayers relies on Vulkan-Headers version from CMake config file
        # to set api_version in its manifest file, but this value MUST have format x.y.z (no extra number).
        # FIXME: find a way to force correct version in CMakeDeps of vulkan-headers recipe?
        # NOTE: At version 1.3.239, the JSON_API_VERSION was removed from the cmakelists file,
        if Version(self.version) >= "1.3.235" and Version(self.version) < "1.3.239":
            vk_version = Version(self.dependencies["vulkan-headers"].ref.version)
            sanitized_vk_version = f"{vk_version.major}.{vk_version.minor}.{vk_version.patch}"
            replace_in_file(
                self, os.path.join(self.source_folder, "layers", "CMakeLists.txt"),
                "set(JSON_API_VERSION ${VulkanHeaders_VERSION})",
                f"set(JSON_API_VERSION \"{sanitized_vk_version}\")",
            )
        # FIXME: two CMake module/config files should be generated (SPIRV-ToolsConfig.cmake and SPIRV-Tools-optConfig.cmake),
        # but it can't be modeled right now in spirv-tools recipe
        if not os.path.exists(os.path.join(self.generators_folder, "SPIRV-Tools-optConfig.cmake")):
            shutil.copy(
                os.path.join(self.generators_folder, "SPIRV-ToolsConfig.cmake"),
                os.path.join(self.generators_folder, "SPIRV-Tools-optConfig.cmake"),
            )
        if self.settings.os == "Android":
            # INFO: libVkLayer_utils.a: error: undefined symbol: __android_log_print
            # https://github.com/KhronosGroup/Vulkan-ValidationLayers/commit/a26638ae9fdd8c40b56d4c7b72859a5b9a0952c9
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "VkLayer_utils PUBLIC Vulkan::Headers", "VkLayer_utils PUBLIC Vulkan::Headers -landroid -llog")
        if not self.options.get_safe("fPIC"):
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "CMAKE_POSITION_INDEPENDENT_CODE ON", "CMAKE_POSITION_INDEPENDENT_CODE OFF")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if Version(self.version) >= "1.3.268.0":
            # After this version the utilities library is built but is not part of the distribution
            # (instead it is now part of vulkan-utility-libraries)
            rm(self, "*.a", self.package_folder)
            rm(self, "*.lib", self.package_folder)

        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
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
        fix_apple_shared_install_name(self)

    def package_info(self):
        if Version(self.version) < "1.3.268.0":
            self.cpp_info.libs = ["VkLayer_utils"]
        else:
            self.cpp_info.includedirs = []

        manifest_subfolder = "bin" if self.settings.os == "Windows" else os.path.join("res", "vulkan", "explicit_layer.d")
        vk_layer_path = os.path.join(self.package_folder, manifest_subfolder)
        self.runenv_info.prepend_path("VK_LAYER_PATH", vk_layer_path)

        # Update runtime discovery paths to allow libVkLayer_khronos_validation.{so,dll,dylib} to be discovered
        # and loaded by vulkan-loader when the consumer executes
        # This is necessary because this package exports a static lib to link against and a dynamic lib to load at runtime
        runtime_lib_discovery_path = "LD_LIBRARY_PATH"
        if self.settings.os == "Windows":
            runtime_lib_discovery_path = "PATH"
        if self.settings.os == "Macos":
            runtime_lib_discovery_path = "DYLD_LIBRARY_PATH"
        for libdir in [os.path.join(self.package_folder, libdir) for libdir in self.cpp_info.libdirs]:
            self.runenv_info.prepend_path(runtime_lib_discovery_path, libdir)

        if self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["android", "log"])
