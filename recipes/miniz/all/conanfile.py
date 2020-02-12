import glob
import os
import shutil

from conans import ConanFile, CMake, tools

class MinizConan(ConanFile):
    name = "miniz"
    description = "Lossless, high performance data compression library that " \
                  "implements the zlib (RFC 1950) and Deflate (RFC 1951) " \
                  "compressed data format specification standards"
    license = "MIT"
    topics = ("conan", "miniz", "compression", "lossless")
    homepage = "https://github.com/richgel999/miniz"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        cmake.build(target="miniz")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        include_dir = os.path.join(self.package_folder, "include")
        tools.mkdir(include_dir)
        for header_file in glob.glob(os.path.join(self._source_subfolder, "*.h")):
            shutil.copy(header_file, include_dir)

        build_lib_dir = os.path.join(self._build_subfolder, "lib")
        build_bin_dir = os.path.join(self._build_subfolder, "bin")
        self.copy(pattern="*.a", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=build_lib_dir, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=build_bin_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
