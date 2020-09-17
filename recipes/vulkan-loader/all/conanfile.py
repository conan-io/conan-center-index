import os
import glob
from conans import ConanFile, tools, CMake


class VulkanLoaderConan(ConanFile):
    name = "vulkan-loader"
    description = "Khronos official Vulkan ICD desktop loader for Windows, Linux, and MacOS."
    topics = ("conan", "vulkan", "loader", "desktop", "gpu")
    homepage = "https://github.com/KhronosGroup/Vulkan-Loader"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "build_type", "compiler"
    generators = "cmake", "cmake_find_package"
    short_paths = True
    options = {
        "with_wsi_xcb": [True, False],
        "with_wsi_xlib": [True, False],
        "with_wsi_wayland": [True, False],
        "with_wsi_directfb": [True, False],
    }
    default_options = {
        "with_wsi_xcb": False,
        "with_wsi_xlib": False,
        "with_wsi_wayland": False,
        "with_wsi_directfb": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.with_wsi_wayland:
            # TODO wayland package
            self.output.warn("Conan package for Wayland is not available, this package will be used from system.")
        if self.options.with_wsi_directfb:
            # TODO directfb package
            self.output.warn("Conan package for DirectFB is not available, this package will be used from system.")

    def requirements(self):
        self.requires("vulkan-headers/{}".format(self.version))
        if self.settings.os == "Linux" and (self.options.with_wsi_xcb or self.options.with_wsi_xlib):
            self.requires("xorg/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("Vulkan-Loader-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_WSI_XCB_SUPPORT"] = self.options.with_wsi_xcb
        self._cmake.definitions["BUILD_WSI_XLIB_SUPPORT"] = self.options.with_wsi_xlib
        self._cmake.definitions["BUILD_WSI_WAYLAND_SUPPORT"] = self.options.with_wsi_wayland
        self._cmake.definitions["BUILD_WSI_DIRECTFB_SUPPORT"] = self.options.with_wsi_directfb

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
