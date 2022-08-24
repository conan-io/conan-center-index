import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class CargsConan(ConanFile):
    name = "cargs"
    description = "A lightweight getopt replacement that works on Linux, " \
                  "Windows and macOS. Command line argument parser library" \
                  " for C/C++. Can be used to parse argv and argc parameters."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://likle.github.io/cargs/"
    topics = ("cargs", "cross-platform", "windows", "macos", "osx", "linux",
              "getopt", "getopt-long", "command-line-parser", "command-line",
              "arguments", "argument-parser")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared and self.settings.os == "Windows"
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build(target="cargs")

    def package(self):
        include_dir = os.path.join(self._source_subfolder, 'include')
        lib_dir = os.path.join(self._build_subfolder, "lib")
        bin_dir = os.path.join(self._build_subfolder, "bin")

        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("cargs.h", dst="include", src=include_dir)
        self.copy(pattern="*.a", dst="lib", src=lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=lib_dir, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=lib_dir, keep_path=False,
                  symlinks=True)
        self.copy(pattern="*.dll", dst="bin", src=bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
