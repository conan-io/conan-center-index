from conans import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.layout import cmake_layout


class LibnsgifConan(ConanFile):
    name = "libnsgif"
    version = "1.0"

    # Optional metadata
    license = "MIT License"
    #author = ["Richard Wilson <richard.wilson@netsurf-browser.org>", "Sean Fox <dyntryx@gmail.com>", "Michael Drake <tlsa@netsurf-browser.org>"]
    url = "https://github.com/conan-io/conan-center-index"
    description = "GIF decoding library by NetSurf Browser. <http://source.netsurf-browser.org/libnsgif.git/>"
    topics = ("gifs", "decoding")
    homepage = "http://source.netsurf-browser.org/libnsgif.git/"
    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self)

#    def generate(self):
#        tc = CMakeToolchain(self)
#        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libnsgif"]
