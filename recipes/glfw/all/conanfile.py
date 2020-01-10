import os
import glob
from conans import ConanFile, CMake, tools


class GlfwConan(ConanFile):
    name = "glfw"
    description = "GLFW is a free, Open Source, multi-platform library for OpenGL, OpenGL ES and Vulkan" \
                  "application development. It provides a simple, platform-independent API for creating" \
                  "windows, contexts and surfaces, reading input, handling events, etc."
    settings = "os", "arch", "build_type", "compiler"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/glfw/glfw"
    topics = ("conan", "gflw", "opengl", "vulkan", "opengl-es")
    exports = "LICENSE"
    generators = "cmake"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        if self.settings.os == 'Linux':
            pass
            # check system

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _patch_sources(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project(GLFW VERSION 3.3.1 LANGUAGES C)",
            '''project(GLFW VERSION 3.3.1 LANGUAGES C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["GLFW_BUILD_EXAMPLES"] = False
        cmake.definitions["GLFW_BUILD_TESTS"] = False
        cmake.definitions["GLFW_BUILD_DOCS"] = False
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.pdb", dst="bin", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.name = "glfw3"
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append([
                'Xrandr', 'Xrender', 'Xi', 'Xinerama', 'Xcursor', 'GL', 'm',
                'dl', 'drm', 'Xdamage', 'X11-xcb', 'xcb-glx', 'xcb-dri2',
                'xcb-dri3', 'xcb-present', 'xcb-sync', 'Xxf86vm', 'Xfixes',
                'Xext', 'X11', 'pthread', 'xcb', 'Xau'
            ])
            if self.options.shared:
                self.cpp_info.exelinkflags.append("-lrt -lm -ldl")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(
                ["OpenGL", "Cocoa", "IOKit", "CoreVideo"])
