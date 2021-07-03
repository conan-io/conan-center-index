import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

modules_list = ['bullet', 'gel', 'ode']

class Chai3dConan(ConanFile):
    name = "chai3d"
    version = "3.2.0"
    license = "BSD 3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.chai3d.org"
    description = ("An open source set of C++ libraries for computer haptics, "
                   "visualization and interactive real-time simulation.")
    topics = ("conan", "chai3d", "computer haptics", "visualization",
              "interactive real-time simulation")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_utils": [True, False]}
    options.update(
        {"with_{}".format(module): [True, False]
         for module in modules_list})
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_utils": False}
    default_options.update(
        {"with_{}".format(module): True
         for module in modules_list})
    exports_sources = ["CMakeLists.txt", os.path.join("patches", "*.patch")]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        # the following conan dependencies are missing:
        # * core:
        #  - eigen (requires version 3.2.X, so use bundled)
        #  - giflib (requires a version lower than 5.0, so use bundled)
        #  - lib3ds (n/a)
        #  - theoraplayer (n/a)
        # * ode module:
        #  - ode (n/a)
        # * bullet module:
        #  - bullet (requires a specific compiling flag, so use bundled)
        self.requires("opengl/system")
        self.requires("glew/2.2.0")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        self.requires("openal/1.19.1")
        self.requires("pugixml/1.11")
        self.requires("theora/1.1.1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "Macos"]:
            raise ConanInvalidConfiguration(
                "Unsupported System. "
                "This package only supports Windows/Linux/Macos")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")
        if (self.settings.compiler == "gcc" and
            tools.Version(self.settings.compiler.version) < "5"):
            raise ConanInvalidConfiguration("This package requires gcc 5+")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{0}-{1}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)
        if self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            # modules need to know where to find the chai3d core target
            self._cmake.definitions["CHAI3D_DIR"] = os.path.join(
                self.build_folder,
                self._build_subfolder,
                self._source_subfolder)
        self._cmake.definitions["CHAI3D_BUILD_UTILS"] = self.options.build_utils
        # build modules on demand
        for module in modules_list:
            opt_name = "with_{}".format(module)
            opt_value = getattr(self.options, opt_name)
            if opt_value:
                self._cmake.definitions["CHAI3D_{}".format(
                   opt_name.upper())] = opt_value
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("copyright.txt", dst="licenses", src=self._source_subfolder)
        # libs
        self.copy("*chai3d*",
                  dst="lib",
                  src=os.path.join(self._build_subfolder, "lib"),
                  keep_path=False)
        # modules libs (windows only)
        if self.settings.os == "Windows":
            self.copy("*chai3d*.dll",
                  dst="bin",
                  src=os.path.join(self._build_subfolder, "bin"),
                  keep_path=False)
        # headers
        self.copy("*.h",
                  dst="include",
                  src=os.path.join(self._source_subfolder, "src"))
        # Eigen headers
        self.copy("Eigen/*",
                  dst="include",
                  src=os.path.join(self._source_subfolder, "external", "Eigen"))
        # modules headers
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
                if module == "bullet":
                    self.copy("*.h",
                              dst="include",
                              src=os.path.join(mod_path, "external", "bullet",
                                               "src"))
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
        # cli utils
        if self.options.build_utils:
            self.copy("*",
                      dst="bin",
                      src=os.path.join(self._build_subfolder, "bin"))

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
            # set PATH for dlls
            bin_path = os.path.join(self.package_folder, "bin")
            self.env_info.path.append(bin_path)
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(
                ["GL", "GLU", "usb-1.0", "rt", "pthread", "dl"])
            self.cpp_info.defines.append("LINUX")
            self.cpp_info.cxxflags.extend(
                ["-march=native", "-Wno-deprecated", "-std=c++0x"])
            # set ABI compatibility for gcc 5+
            if self.settings.compiler == "gcc":
                if str(self.settings.compiler.libcxx) == "libstdc++":
                    self.cpp_info.defines.append("_GLIBCXX_USE_CXX11_ABI=0")
                elif str(self.settings.compiler.libcxx) == "libstdc++11":
                    self.cpp_info.defines.append("_GLIBCXX_USE_CXX11_ABI=1")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = [
                "OpenGL", "CoreFoundation", "IOKit", "CoreServices",
                "CoreAudio", "AudioToolbox", "AudioUnit"
            ]
            self.cpp_info.defines.append("MACOSX")
            self.cpp_info.cxxflags.extend([
                "-Qunused-arguments", "-Wno-deprecated", "-std=c++0x",
                "-stdlib=libc++11"
            ])
