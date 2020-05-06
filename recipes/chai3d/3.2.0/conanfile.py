import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

modules_list = ['bullet', 'gel', 'ode']


class Chai3dConan(ConanFile):
    name = "chai3d"
    license = "BSD 3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.chai3d.org"
    description = ("An open source set of C++ libraries for computer haptics, "
                   "visualization and interactive real-time simulation.")
    topics = ("conan", "chai3d", "computer haptics", "visualization",
              "interactive real-time simulation")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    options = {"shared": [True, False], "fPIC": [True, False]}
    options.update(
        {"with_{}".format(module): [True, False]
         for module in modules_list})
    default_options = {"shared": False, "fPIC": True}
    default_options.update(
        {"with_{}".format(module): False
         for module in modules_list})
    exports_sources = ["CMakeLists.txt", os.path.join("patches", "*.patch")]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _platform_path(self):
        if self.settings.os == "Windows":
            os_name = "win"
            arch_name = ("Win32", "x64")[self.settings.arch == "x86_64"]
        elif self.settings.os == "Linux":
            os_name = "lin"
            arch_name = ("i686", "x86_64")[self.settings.arch == "x86_64"]
        elif self.settings.os == "Macos":
            os_name = "mac"
            arch_name = ("i386", "x86_64")[self.settings.arch == "x86_64"]
        return "{0}-{1}".format(os_name, arch_name)

    def requirements(self):
        # the following conan dependencies are missing:
        # * core:
        #  - giflib: available version (5.1.7) crashes during compilation
        #  - lib3ds: not available in conan center
        # * ode module:
        #  - ode: not available in conan center
        self.requires.add("eigen/3.3.7")
        self.requires.add("glew/2.1.0@bincrafters/stable")
        self.requires.add("libjpeg/9d")
        self.requires.add("libpng/1.6.37")
        self.requires.add("openal/1.19.1")
        self.requires.add("pugixml/1.10@bincrafters/stable")
        self.requires.add("theora/1.1.1@bincrafters/stable")
        if self.options.with_bullet:
            self.requires.add("bullet3/2.89")

    def configure(self):
        if self.settings.os not in ["Windows", "Linux", "Macos"]:
            raise ConanInvalidConfiguration(
                "Unsupported System. "
                "This package only supports Windows/Linux/Macos")
        elif (self.settings.os == "Windows"
              and self.settings.compiler == "Visual Studio"
              and tools.Version(self.settings.compiler.version) <= "8"):
            raise ConanInvalidConfiguration(
                "Unsupported Visual Studio version. "
                "This package requires Visual Studio editions "
                "2010 or later")
        elif (self.settings.os == "Macos"
              and tools.Version(self.settings.os.version) <= "10.8"):
            raise ConanInvalidConfiguration(
                "Unsupported Macos version. "
                "This package requires Macos version "
                "10.9 or later")
        # chai3d builds with the std c++0x so we warn the user for a
        # potential ABI incompatibility
        if self.settings.compiler != "Visual Studio":
            tools.check_min_cppstd(self, "11")
        if (self.settings.compiler == "gcc"
                and Version(self.settings.compiler.version) >= "5"
                and self.settings.compiler.libcxx == "libstdc++"):
            raise ConanInvalidConfiguration(
                "Unsupported compiler configuration. "
                "This package uses the c++0x standard and thus requires "
                "compiler.libcxx=libstdc++11")

    def config_options(self):
        if self.options.shared or self.settings.os == "Windows":
            del self.options.fPIC
        # glew doesn't have an fPIC option, so its type must match with chai3d
        self.options["glew"].shared = self.options.shared

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def build(self):
        cmake = CMake(self)
        # build modules on demand
        for module in modules_list:
            opt_name = "with_{}".format(module)
            opt_value = getattr(self.options, opt_name)
            if opt_value:
                cmake.definitions["CHAI3D_{}".format(
                    opt_name.upper())] = opt_value
        # modules need to know where to find the chai3d core targets
        cmake.definitions["CHAI3D_DIR"] = os.path.join(self.build_folder,
                                                       self._source_subfolder)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("copyright.txt", dst="licenses", src=self._source_subfolder)
        # libs
        self.copy("libchai3d*",
                  dst="lib",
                  src=os.path.join(self.build_folder, "lib"),
                  keep_path=False)
        # headers
        self.copy("*.h",
                  dst="include",
                  src=os.path.join(self._source_subfolder, "src"))
        # modules headers
        for module in modules_list:
            if getattr(self.options, "with_{}".format(module)):
                mod_path = os.path.join(self._source_subfolder, "modules",
                                        module.upper())
                self.copy("*.h",
                          dst="include",
                          src=os.path.join(mod_path, "src"))
                if module == "ode":
                    self.copy("*.h",
                              dst="include",
                              src=os.path.join(mod_path, "external", "ODE",
                                               "include"))
        # DHD dependency
        if self.settings.os != "Windows":
            self.copy("libdrd.a",
                      dst="lib",
                      src=os.path.join(self._source_subfolder, "external",
                                       "DHD", "lib", self._platform_path))
        # dynamic libs needed by the executables
        if self.settings.os != "Linux":
            self.copy("*",
                      dst="bin",
                      src=os.path.join(self._source_subfolder, "bin",
                                       self._platform_path))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        # match chai3d export options
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["opengl32", "glu32", "winmm"])
            if self.settings.compiler == "Visual Studio":
                self.cpp_info.defines.append("_CRT_SECURE_NO_DEPRECATED")
                self.cpp_info.cxxflags.extend(["/EHsc", "/MP"])
                arch_def = ("WIN64", "WIN32")[self.settings.arch == "x86_64"]
                self.cpp_info.defines.append(arch_def)
            elif self.settings.compiler == "mingw":
                self.cpp_info.defines.append("WIN32")
            self.cpp_info.cxxflags.extend(
                ["-march=native", "-Wno-deprecated", "-std=c++0x"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(
                ["GL", "GLU", "usb-1.0", "rt", "pthread", "dl"])
            self.cpp_info.defines.append("LINUX")
            self.cpp_info.cxxflags.extend(
                ["-march=native", "-Wno-deprecated", "-std=c++0x"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = [
                "OpenGL", "CoreFoundation", "IOKit", "CoreServices",
                "CoreAudio", "AudioToolbox", "AudioUnit"
            ]
            self.cpp_info.defines.append("MACOSX")
            self.cpp_info.cxxflags.extend([
                "-Qunused-arguments", "-Wno-deprecated", "-std=c++0x",
                "-stdlib=libc++"
            ])
