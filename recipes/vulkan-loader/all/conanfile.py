import os
import glob
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class VulkanLoaderConan(ConanFile):
    name = "vulkan-loader"
    description = "Khronos official Vulkan ICD desktop loader for Windows, Linux, and MacOS."
    topics = ("conan", "vulkan", "loader", "desktop", "gpu")
    homepage = "https://github.com/KhronosGroup/Vulkan-Loader"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_wsi_xcb": [True, False],
        "with_wsi_xlib": [True, False],
        "with_wsi_wayland": [True, False],
        "with_wsi_directfb": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_wsi_xcb": True,
        "with_wsi_xlib": True,
        "with_wsi_wayland": True,
        "with_wsi_directfb": False,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "pkg_config"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland
            del self.options.with_wsi_directfb
        # default shared on non-Apple OS
        if not tools.is_apple_os(self.settings.os):
            self.options.shared = True

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.get_safe("with_wsi_directfb"):
            # TODO: directfb package
            raise ConanInvalidConfiguration("Conan recipe for DirectFB is not available yet.")
        if not tools.is_apple_os(self.settings.os) and not self.options.shared:
            raise ConanInvalidConfiguration("Static builds are not supported on {}".format(self.settings.os))
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < 15:
            # FIXME: It should build but Visual Studio 2015 container in CI of CCI seems to lack some Win SDK headers
            raise ConanInvalidConfiguration("Visual Studio < 2017 not yet supported in this recipe")

    def requirements(self):
        self.requires("vulkan-headers/{}".format(self.version))
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib"):
            self.requires("xorg/system")
        if self.options.get_safe("with_wsi_wayland"):
            self.requires("wayland/1.18.0")

    def build_requirements(self):
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib") or \
           self.options.get_safe("with_wsi_wayland") or self.options.get_safe("with_wsi_directfb"):
            self.build_requires("pkgconf/1.7.3")
        if self._is_mingw:
            self.build_requires("jwasm/2.13")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("Vulkan-Loader-*")[0], self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "FindVulkanHeaders.cmake"),
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/share/vulkan/registry",
                              "HINTS ${VULKAN_HEADERS_INSTALL_DIR}/res/vulkan/registry")
        # Honor settings.compiler.runtime
        tools.replace_in_file(os.path.join(self._source_subfolder, "loader", "CMakeLists.txt"),
                              "if(${configuration} MATCHES \"/MD\")",
                              "if(FALSE)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["VULKAN_HEADERS_INSTALL_DIR"] = self.deps_cpp_info["vulkan-headers"].rootpath
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["USE_CCACHE"] = False
        if self.settings.os == "Linux":
            self._cmake.definitions["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
            self._cmake.definitions["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
            self._cmake.definitions["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
            self._cmake.definitions["BUILD_WSI_DIRECTFB_SUPPORT"] = self.options.with_wsi_directfb
        if self.settings.os == "Windows":
            self._cmake.definitions["ENABLE_WIN10_ONECORE"] = False
        if tools.is_apple_os(self.settings.os):
            self._cmake.definitions["BUILD_STATIC_LOADER"] = not self.options.shared
        self._cmake.definitions["BUILD_LOADER"] = True
        if self.settings.os == "Windows":
            self._cmake.definitions["USE_MASM"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        if self.deps_cpp_info["vulkan-headers"].version != self.version:
            raise ConanInvalidConfiguration("vulkan-loader must be built with the same version than vulkan-headers.")
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "loader"))

    def package_info(self):
        if self.deps_cpp_info["vulkan-headers"].version != self.version:
            self.output.warn("vulkan-headers version is different than vulkan-loader. Several symbols might be missing.")

        self.cpp_info.names["cmake_find_package"] = "Vulkan"
        self.cpp_info.names["cmake_find_package_multi"] = "Vulkan"
        self.cpp_info.names["pkg_config"] = "vulkan"
        suffix = "-1" if self.settings.os == "Windows" else ""
        self.cpp_info.libs = ["vulkan" + suffix]
        self.cpp_info.includedirs = self.deps_cpp_info["vulkan-headers"].include_paths # allow to properly set Vulkan_INCLUDE_DIRS in cmake_find_package(_multi) generators
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread", "m"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation"]

        vulkan_sdk_path = self.package_folder
        self.output.info("Create VULKAN_SDK environment variable: {}".format(vulkan_sdk_path))
        self.env_info.VULKAN_SDK = vulkan_sdk_path
