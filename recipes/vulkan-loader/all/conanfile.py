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
        "shared": True,
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
    def _apple_os(self):
        return ["Macos", "iOS", "watchOS", "tvOS"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_wsi_xcb
            del self.options.with_wsi_xlib
            del self.options.with_wsi_wayland
            del self.options.with_wsi_directfb

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Linux":
            if self.options.with_wsi_wayland:
                # TODO wayland package
                self.output.warn("Conan package for Wayland is not available, this package will be used from system.")
            if self.options.with_wsi_directfb:
                # TODO directfb package
                self.output.warn("Conan package for DirectFB is not available, this package will be used from system.")

        if self.settings.os not in self._apple_os and not self.options.shared:
            raise ConanInvalidConfiguration("Static builds are not supported on {}".format(self.settings.os))

    def requirements(self):
        self.requires("vulkan-headers/{}".format(self.version))
        if self.settings.os == "Linux":
            if self.options.with_wsi_xcb or self.options.with_wsi_xlib:
                self.requires("xorg/system")
            if self.options.with_wsi_wayland:
                self.requires("wayland/1.18.0")

    def build_requirements(self):
        if self.options.get_safe("with_wsi_xcb") or self.options.get_safe("with_wsi_xlib") or \
           self.options.get_safe("with_wsi_wayland") or self.options.get_safe("with_wsi_directfb"):
            self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("Vulkan-Loader-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        if self.settings.os == "Linux":
            self._cmake.definitions["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
            self._cmake.definitions["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
            self._cmake.definitions["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
            self._cmake.definitions["BUILD_WSI_DIRECTFB_SUPPORT"] = self.options.with_wsi_directfb
        if self.settings.os in self._apple_os:
            self._cmake.definitions["BUILD_STATIC_LOADER"] = not self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "loader"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "vulkan"
        self.cpp_info.filenames["cmake_find_package"] = "VulkanLoader"
        self.cpp_info.filenames["cmake_find_package_multi"] = "VulkanLoader"
        self.cpp_info.names["cmake_find_package"] = "Vulkan"
        self.cpp_info.names["cmake_find_package_multi"] = "Vulkan"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os != "Windows":
            self.cpp_info.system_libs = ["dl", "pthread", "m"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation"]
