from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"

class Utf8ProcConan(ConanFile):
    name = "utf8proc"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JuliaStrings/utf8proc"
    description = "A clean C library for processing UTF-8 Unicode data"
    topics = ("utf", "utf8", "unicode", "text")
    license = "MIT expat"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libutf8proc"
        self.cpp_info.libs = ["utf8proc_static" if self.settings.compiler == "Visual Studio" and not self.options.shared else "utf8proc"]
        if not self.options.shared:
            self.cpp_info.defines = ["UTF8PROC_STATIC"]
