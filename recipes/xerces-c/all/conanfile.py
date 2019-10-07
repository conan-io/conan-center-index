# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class XercesCConan(ConanFile):
    name = "xerces-c"
    description = "Xerces-C++ is a validating XML parser written in a portable subset of C++"
    topics = ("conan", "xerces", "XML", "validation", "DOM", "SAX", "SAX2")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://xerces.apache.org/xerces-c/index.html"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        # https://xerces.apache.org/xerces-c/build-3.html
        # TODO : check if we need options for that variants
        cmake.definitions["network-accessor"] = {"Windows": "winsock",
                                                 "Macos": "cfurl",
                                                 "Linux": "socket"}.get(str(self.settings.os))
        cmake.definitions["transcoder"] = {"Windows": "windows",
                                           "Macos": "macosunicodeconverter",
                                           "Linux": "gnuiconv"}.get(str(self.settings.os))
        cmake.definitions["message-loader"] = "inmemory"
        cmake.definitions["xmlch-type"] = "uint16_t"
        cmake.definitions["mutex-manager"] = {"Windows": "windows",
                                              "Macos": "posix",
                                              "Linux": "posix"}.get(str(self.settings.os))
        # avoid picking up system dependency
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_CURL'] = True
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_ICU'] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))

    def package_info(self):
        version_tokens = self.version.split(".")
        if self.settings.os == "Windows":
            lib = "xerces-c_%s" % version_tokens[0]
            if self.settings.build_type == "Debug":
                lib += "d"
            self.cpp_info.libs = [lib]
        else:
            self.cpp_info.libs = ["xerces-c" if self.options.shared else
                                  ("xerces-c-%s.%s" % (version_tokens[0], version_tokens[1]))]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ['CoreFoundation', 'CoreServices']
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
