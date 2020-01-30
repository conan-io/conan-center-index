import os
from conans import ConanFile, CMake, tools


class CwalkConan(ConanFile):
    name = "cwalk"
    description = "Path library for C/C++. Cross-Platform for Windows, " \
                  "MacOS and Linux. Supports UNIX and Windows path styles " \
                  "on those platforms."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://likle.github.io/cwalk/"
    topics = ("cwalk", "cross-platform", "windows", "macos", "osx", "linux",
              "path-manipulation", "path", "directory", "file", "file-system",
              "unc", "path-parsing", "file-path")
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build(target="cwalk")

    def package(self):
        include_dir = os.path.join(self._source_subfolder, 'include')
        lib_dir = os.path.join(self._build_subfolder, "lib")
        bin_dir = os.path.join(self._build_subfolder, "bin")

        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("cwalk.h", dst="include", src=include_dir)
        self.copy(pattern="*.a", dst="lib", src=lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=lib_dir, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=lib_dir, keep_path=False,
                  symlinks=True)
        self.copy(pattern="*.dll", dst="bin", src=bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
