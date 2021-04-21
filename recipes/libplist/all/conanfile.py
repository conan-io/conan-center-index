from conans import ConanFile, CMake, tools
import os


class LibplistConan(ConanFile):
    name = "libplist"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libimobiledevice-win32/libplist"
    description = "A library to handle Apple Property List format in binary or XML"
    topics = ["conan", "plist", "apple"]
    license = "LGPL-2.1"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libplist-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["plist", "cnary"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append('pthread')
