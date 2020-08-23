import os
from conans import CMake, ConanFile, tools


class Utf8ProcConan(ConanFile):
    name = "utf8proc"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JuliaStrings/utf8proc"
    description = "A clean C library for processing UTF-8 Unicode data"
    topics = ("utf", "utf8", "unicode", "text")
    license = "MIT expat"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
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
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

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

    def package_info(self):
        self.cpp_info.libs = ["utf8proc_static" if self.settings.compiler == "Visual Studio" and not self.options.shared else "utf8proc"]
        if not self.options.shared:
            self.cpp_info.defines = ["UTF8PROC_STATIC"]
