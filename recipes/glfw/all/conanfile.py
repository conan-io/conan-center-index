import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException


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
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def _check_system_libs(self, libs, install_command):
        installer = tools.SystemPackageTool()
        missing_system_libs=[]
        for package_name in libs:
            if not installer.installed(package_name):
                missing_system_libs.append(package_name)
        if len(missing_system_libs) > 0:
            raise ConanException(
                'System libraries missing: {0} not found. You can install using: "sudo {1} {0}"'
                .format(" ".join(missing_system_libs), install_command))

    def system_requirements(self):
        if self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            libs_name = ""
            os_info = tools.OSInfo()
            if os_info.with_apt:
                libs_name = "libx11-dev libxrandr-dev libxinerama-dev libxkbcommon-dev libxcursor-dev " \
                            "libxi-dev libglu1-mesa-dev"
            elif os_info.with_yum:
                libs_name = "libX11-devel libXrandr-devel libXinerama-devel libxkbcommon-devel " \
                            "libXcursor-devel libXi-devel mesa-libGL-devel"
            elif os_info.with_pacman:
                libs_name = "libx11 libxrandr libxinerama libxkbcommon-x11 libxcursor libxi libglvnd "
            else:
                self.output.warn("Could not find any package manager, please install x11, xrandr, xinerama," \
                                 "xkb, xcursor, xi and mesa libraries if not already installed.")
                return
            package_tool.install(update=True, packages=libs_name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

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
        cmake = self._configure_cmake()
        cmake.build()
        if self.settings.os == "Macos" and self.options.shared:
            with tools.chdir(os.path.join(self._source_subfolder, 'src')):
                for filename in glob.glob('*.dylib'):
                    self.run('install_name_tool -id {filename} {filename}'.format(filename=filename))

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.pdb", dst="bin", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['X11', 'GL', 'm', 'dl', 'pthread'])
            if self.options.shared:
                self.cpp_info.exelinkflags.append("-lrt -lm -ldl")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(
                ["OpenGL", "Cocoa", "IOKit", "CoreVideo"])
