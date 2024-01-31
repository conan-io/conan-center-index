from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class VulkanLoaderConan(ConanFile):
    name = "vulkan-loader"
    description = "Khronos official Vulkan ICD desktop loader for Windows, Linux, and MacOS."
    topics = ("vulkan", "loader", "desktop", "gpu")
    homepage = "https://github.com/KhronosGroup/Vulkan-Loader"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_wsi_xcb": [True, False],
        "with_wsi_xlib": [True, False],
        "with_wsi_wayland": [True, False],
        "with_wsi_directfb": [True, False],
    }
    default_options = {
        "with_wsi_xcb": True,
        "with_wsi_xlib": True,
        "with_wsi_wayland": True,
        "with_wsi_directfb": False,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _is_pkgconf_needed(self):
        return self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib") or \
               self.options.get_safe("with_wsi_wayland") or self.options.get_safe("with_wsi_directfb")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland
            del self.options.with_wsi_directfb

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if Version(self.version) < "1.3.231" and self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.22.0")

    def validate(self):
        if self.options.get_safe("with_wsi_directfb"):
            # TODO: directfb package
            raise ConanInvalidConfiguration("Conan recipe for DirectFB is not available yet.")
        # FIXME: It should build but Visual Studio 2015 container in CI of CCI seems to lack some Win SDK headers
        check_min_vs(self, "191")
        # TODO: to replace by some version range check
        if self.dependencies["vulkan-headers"].ref.version != self.version:
            self.output.warning("vulkan-loader should be built & consumed with the same version than vulkan-headers.")

    def build_requirements(self):
        if self._is_pkgconf_needed:
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.1.0")
        if self._is_mingw:
            self.tool_requires("jwasm/2.13")
        if Version(self.version) >= "1.3.234":
            self.tool_requires("cmake/[>=3.17.2 <4.0]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self._is_pkgconf_needed or self._is_mingw:
            env = VirtualBuildEnv(self)
            env.generate()

        tc = CMakeToolchain(self)
        tc.variables["VULKAN_HEADERS_INSTALL_DIR"] = self.dependencies["vulkan-headers"].package_folder.replace("\\", "/")
        tc.variables["BUILD_TESTS"] = False
        tc.variables["USE_CCACHE"] = False
        if self.settings.os == "Linux":
            tc.variables["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
            tc.variables["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
            tc.variables["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
            tc.variables["BUILD_WSI_DIRECTFB_SUPPORT"] = self.options.with_wsi_directfb
        if self.settings.os == "Windows":
            tc.variables["ENABLE_WIN10_ONECORE"] = False
        tc.variables["BUILD_LOADER"] = True
        if self.settings.os == "Windows":
            tc.variables["USE_MASM"] = True
        if Version(self.version) >= "1.3.212":
            tc.variables["ENABLE_WERROR"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        if self._is_pkgconf_needed:
            pkg = PkgConfigDeps(self)
            pkg.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        if Version(self.version) < "1.3.234":
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "FindVulkanHeaders.cmake"),
                                  "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/share/vulkan/registry",
                                  "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/res/vulkan/registry")

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")

        # Honor settings.compiler.runtime
        if Version(self.version) < "1.3.254":
            replace_in_file(self, os.path.join(self.source_folder, "loader", "CMakeLists.txt"),
                                  "if(${configuration} MATCHES \"/MD\")",
                                  "if(FALSE)")
        else:
            replace_in_file(
                self,
                cmakelists,
                "set(TESTS_STANDARD_CXX_PROPERTIES ${LOADER_STANDARD_CXX_PROPERTIES} MSVC_RUNTIME_LIBRARY \"MultiThreaded$<$<CONFIG:Debug>:Debug>DLL\")",
                "set(TESTS_STANDARD_CXX_PROPERTIES ${LOADER_STANDARD_CXX_PROPERTIES})",
            )
            replace_in_file(
                self,
                cmakelists,
                "set(CMAKE_MSVC_RUNTIME_LIBRARY \"MultiThreaded$<$<CONFIG:Debug>:Debug>\")",
                "",
            )

        # No warnings as errors
        if Version(self.version) < "1.3.212":
            replace_in_file(self, cmakelists, "/WX", "")
        # This fix is needed due to CMAKE_FIND_PACKAGE_PREFER_CONFIG ON in CMakeToolchain (see https://github.com/conan-io/conan/issues/10387).
        # Indeed we want to use upstream Find modules of xcb, x11, wayland and directfb. There are properly using pkgconfig under the hood.
        if Version(self.version) < "1.3.234":
            replace_in_file(self, cmakelists, "find_package(XCB REQUIRED)", "find_package(XCB REQUIRED MODULE)")
            replace_in_file(self, cmakelists, "find_package(X11 REQUIRED)", "find_package(X11 REQUIRED MODULE)")
        # find_package(Wayland REQUIRED) was removed, as it was unused
        if Version(self.version) < "1.3.231":
            replace_in_file(self, cmakelists, "find_package(Wayland REQUIRED)", "find_package(Wayland REQUIRED MODULE)")
        if Version(self.version) < "1.3.234":
            replace_in_file(self, cmakelists, "find_package(DirectFB REQUIRED)", "find_package(DirectFB REQUIRED MODULE)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "loader"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Vulkan")
        self.cpp_info.set_property("cmake_file_name", "VulkanLoader")
        self.cpp_info.set_property("cmake_module_target_name", "Vulkan::Vulkan")
        self.cpp_info.set_property("cmake_target_name", "Vulkan::Loader")
        self.cpp_info.set_property("pkg_config_name", "vulkan")
        suffix = "-1" if self.settings.os == "Windows" else ""
        self.cpp_info.libs = [f"vulkan{suffix}"]

        # allow to properly set Vulkan_INCLUDE_DIRS in FindVulkan.cmake
        self.cpp_info.includedirs = self.dependencies["vulkan-headers"].cpp_info.aggregated_components().includedirs

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "pthread", "m"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation"]
