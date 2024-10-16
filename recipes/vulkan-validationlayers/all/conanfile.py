from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, mkdir, rename, replace_in_file, rm
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
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
    package_type = "application"
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
    def _needs_pkg_config(self):
        return self.options.get_safe("with_wsi_xcb") or \
               self.options.get_safe("with_wsi_xlib")

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "9",
            "clang": "6",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15.7",
        }

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _vulkan_sdk_version(self):
        return self.version

    def requirements(self):
        self.requires(f"spirv-headers/{self._vulkan_sdk_version}")
        self.requires(f"spirv-tools/{self._vulkan_sdk_version}", visible=False)
        self.requires(f"vulkan-headers/{self._vulkan_sdk_version}", transitive_headers=True)
        if Version(self.version) >= "1.3.268.0":
            self.requires(f"vulkan-utility-libraries/{self._vulkan_sdk_version}")

        self.requires("robin-hood-hashing/3.11.5")
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.22.0")

        # TODO: add support for mimalloc

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration("vulkan-validationlayers can't depend on shared spirv-tools")

    def build_requirements(self):
        if self._needs_pkg_config and not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if Version(self.version) >= "1.3.239":
            self.tool_requires("cmake/[>=3.17.2 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
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
        # Suppress overly noisy warnings
        # tc.extra_cxxflags.append("-w")
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        if self._needs_pkg_config:
            deps = PkgConfigDeps(self)
            deps.generate()

    def _patch_sources(self):
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
        if Version(self.version) < "1.3.250.0":
            replace_in_file(self, os.path.join(self.source_folder, "layers", "CMakeLists.txt"),
                            "find_package(PythonInterp 3 QUIET)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
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
        # The output of the package is a VkLayer_khronos_validation runtime library.

        if Version(self.version) >= "1.3.268.0":
            # v1.3.268+ links the VkLayer_utils library statically into the VkLayer_khronos_validation library.
            # Headers have been moved to vulkan-utility-libraries.
            self.cpp_info.includedirs = []
            if is_msvc(self):
                self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs.append("VkLayer_utils")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl"]

        if self.settings.os == "Windows":
            manifest_subfolder = "bin"
        else:
            manifest_subfolder = os.path.join("res", "vulkan", "explicit_layer.d")
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

        # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
        self.env_info.VK_LAYER_PATH.append(vk_layer_path)

        if self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["android", "log"])

        self.cpp_info.requires.append("spirv-headers::spirv-headers")
        self.cpp_info.requires.append("vulkan-headers::vulkan-headers")
        if Version(self.version) >= "1.3.268.0":
            self.cpp_info.requires.append("vulkan-utility-libraries::vulkan-utility-libraries")
        self.cpp_info.requires.append("robin-hood-hashing::robin-hood-hashing")
        if self.options.get_safe("with_wsi_xlib"):
            self.cpp_info.requires.append("xorg::x11")
        if self.options.get_safe("with_wsi_xcb"):
            self.cpp_info.requires.append("xorg::xcb")
        if self.options.get_safe("with_wsi_wayland"):
            self.cpp_info.requires.append("wayland::wayland-client")
