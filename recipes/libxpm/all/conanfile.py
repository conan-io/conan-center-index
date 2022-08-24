import functools
import os

from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class LibXpmConan(ConanFile):
    name = "libxpm"
    description = "X Pixmap (XPM) image file format library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/xorg/lib/libxpm"
    topics = "xpm"
    license = "MIT-open-group"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "windows/*"
    no_copy_source = True

    def validate(self):
        if self.settings.os not in ("Windows", "Linux", "FreeBSD"):
            raise ConanInvalidConfiguration(
                "libXpm is supported only on Windows, Linux and FreeBSD"
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("xorg/system")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_libXpm_VERSION"] = self.version
        cmake.configure()
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self.copy("COPYING", "licenses")
        self.copy("COPYRIGHT", "licenses")
        self._configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["Xpm"]
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["FOR_MSW"]
