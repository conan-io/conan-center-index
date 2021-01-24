from conans import ConanFile, CMake, tools
import os

class NotcursesConan(ConanFile):
    name = "notcurses"
    description = "a blingful TUI/character graphics library"
    topics = ("graphics", "curses", "tui", "console", "ncurses")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nick-black.com/dankwiki/index.php/Notcurses"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False,
                       "readline:with_library":"curses"
                      }
    generators = "cmake", "pkg_config"

    _cmake = None

    def requirements(self):
        self.requires("openimageio/2.2.7.0")
        self.requires("libunistring/0.9.10")
        self.requires("readline/8.0")
        self.requires("ncurses/6.2")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.definitions["USE_MULTIMEDIA"] = "oiio"
        self._cmake.definitions["USE_PANDOC"] = "OFF"
        self._cmake.definitions["USE_POC"] = "OFF"
        self._cmake.definitions["USE_QRCODEGEN"] = "OFF"
        self._cmake.definitions["USE_STATIC"] = not self.options.shared
        self._cmake.configure(source_folder="notcurses-" + self.version)
        return self._cmake

    def package_info(self):
        self.cpp_info.names = "Notcurses"
        self.cpp_info.components["notcurses-core"].names["cmake"] = "NotcursesCore"
        self.cpp_info.components["notcurses-core"].libs = ["libnotcurses-core"]
        self.cpp_info.components["notcurses"].names["cmake"] = "Notcurses"
        self.cpp_info.components["notcurses"].libs = ["libnotcurses"]
        self.cpp_info.components["notcurses"].requires = ["notcurses-core"]
        self.cpp_info.components["notcurses++"].names["cmake"] = "Notcurses++"
        self.cpp_info.components["notcurses++"].libs = ["libnotcurses++"]
        self.cpp_info.components["notcurses++"].requires = ["notcurses"]
