from conans import ConanFile, CMake
from conans.tools import download, unzip, replace_in_file, remove_files_by_mask, get
import os

class ZlibNgConan(ConanFile):
    name = "zlib-ng"
    description = "zlib data compression library for the next generation systems"
    url = "https://github.com/conan-io/conan-center-index"
    homepage="https://github.com/Dead2/zlib-ng/"
    license="https://github.com/Dead2/zlib-ng/blob/ba7f0eb6e294306ac6d771216ea4442f2ea2d830/LICENSE.md"
    topics = ("conan", "zlib", "compression")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        get(**self.conan_data["sources"][self.version])
        os.rename("zlib-ng-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ZLIB_COMPAT"] = False
            self._cmake.definitions["ZLIB_ENABLE_TESTS"] = False
            self._cmake.definitions["WITH_GZFILEOP"] = True
            self._cmake.definitions["WITH_OPTIM"] = True
            self._cmake.definitions["WITH_NEW_STRATEGIES"] = True
            self._cmake.definitions["WITH_NATIVE_INSTRUCTIONS"] = False
            self._cmake.definitions["WITH_SANITIZER"] = False
            self._cmake.definitions["WITH_FUZZERS"] = False
            self._cmake.definitions["WITH_MAINTAINER_WARNINGS"] = False
            self._cmake.definitions["WITH_CODE_COVERAGE"] = False

            self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ZLIB"
        self.cpp_info.names["cmake_find_package_multi"] = "ZLIB"
        if self.settings.os == "Windows":
            if self.options.shared:
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs = ["zlibd"]
                else:
                    self.cpp_info.libs = ["zlib"]
            else:
                if self.settings.build_type == "Debug":
                    self.cpp_info.libs = ["zlibstaticd"]
                else:
                    self.cpp_info.libs = ["zlibstatic"]
        else:
            self.cpp_info.libs = ["z-ng"]

    def _rename_libraries(self):
        if self.settings.os == "Windows":
            lib_path = os.path.join(self.package_folder, "lib")
            suffix = "d" if self.settings.build_type == "Debug" else ""

            if self.options.shared:
                if self.settings.compiler == "Visual Studio":
                    current_lib = os.path.join(lib_path, "zlib%s.lib" % suffix)
                    os.rename(current_lib, os.path.join(lib_path, "zlib.lib"))
            else:
                if self.settings.compiler == "Visual Studio":
                    current_lib = os.path.join(lib_path, "zlibstatic%s.lib" % suffix)
                    os.rename(current_lib, os.path.join(lib_path, "zlib.lib"))
                elif self.settings.compiler == "gcc":
                    current_lib = os.path.join(lib_path, "libzlibstatic.a")
                    os.rename(current_lib, os.path.join(lib_path, "libzlib.a"))
                elif self.settings.compiler == "clang":
                    current_lib = os.path.join(lib_path, "zlibstatic.lib")
                    os.rename(current_lib, os.path.join(lib_path, "zlib.lib"))

    def package(self):
        # Copy license
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)

        # Copy headers
        for header in ["*zlib.h", "*zconf.h"]:
            self.copy(pattern=header, dst="include", src=self._source_subfolder, keep_path=False)
            self.copy(pattern=header, dst="include", src=self._build_subfolder, keep_path=False)

        # Copying static and dynamic libs
        if self.options.shared:
            self.copy(pattern="*.dylib*", dst="lib", src=self._build_subfolder, keep_path=False, symlinks=True)
            self.copy(pattern="*.so*", dst="lib", src=self._build_subfolder, keep_path=False, symlinks=True)
            self.copy(pattern="*.dll", dst="bin", src=self._build_subfolder, keep_path=False)
            self.copy(pattern="*.dll.a", dst="lib", src=self._build_subfolder, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src=self._build_subfolder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=self._build_subfolder, keep_path=False)

        self._rename_libraries()
