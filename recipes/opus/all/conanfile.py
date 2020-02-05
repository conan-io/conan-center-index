from conans import ConanFile, tools, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration

import os
import shutil


class OpusConan(ConanFile):
    name = "opus"
    description = "Opus is a totally open, royalty-free, highly versatile audio codec."
    topics = ("conan", "opus", "audio", "decoder", "decoding", "multimedia", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opus-codec.org"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt","opus_buildtype.cmake"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "fixed_point": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'fixed_point': False}

    _source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("On Windows, the opus package can only be built with "
                                            "Visual Studio 2015 or higher.")

    def config_options(self):
        if self.settings.os == "Windows":
             del self.options.fPIC


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # They forgot to package that file into the tarball for 1.3.1
        # See https://github.com/xiph/opus/issues/129
        os.rename("opus_buildtype.cmake", os.path.join(self._source_subfolder , "opus_buildtype.cmake"))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OPUS_FIXED_POINT"] = self.options.fixed_point
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

    def package_info(self):
        self.cpp_info.names['cmake_find_package'] = 'OPUS'
        self.cpp_info.names['cmake_find_package_multi'] = 'OPUS'
        self.cpp_info.names['pkg_config'] = 'opus'
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Linux' or self.settings.os == "Android":
            self.cpp_info.system_libs.append('m')
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.cpp_info.system_libs.append("ssp")
        self.cpp_info.includedirs.append(os.path.join('include', 'opus'))
