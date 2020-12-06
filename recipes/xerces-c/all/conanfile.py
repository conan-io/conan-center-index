from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
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
        if self.settings.os not in ("Windows", "Macos", "Linux"):
            raise ConanInvalidConfiguration("OS is not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # https://xerces.apache.org/xerces-c/build-3.html
        self._cmake.definitions["network-accessor"] = {"Windows": "winsock",
                                                       "Macos": "cfurl",
                                                       "Linux": "socket"}.get(str(self.settings.os))
        self._cmake.definitions["transcoder"] = {"Windows": "windows",
                                                 "Macos": "macosunicodeconverter",
                                                 "Linux": "gnuiconv"}.get(str(self.settings.os))
        self._cmake.definitions["message-loader"] = "inmemory"
        self._cmake.definitions["xmlch-type"] = "uint16_t"
        self._cmake.definitions["mutex-manager"] = {"Windows": "windows",
                                                    "Macos": "posix",
                                                    "Linux": "posix"}.get(str(self.settings.os))
        # avoid picking up system dependency
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_CURL"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ICU"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "CoreServices"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.names["cmake_find_package"] = "XercesC"
        self.cpp_info.names["cmake_find_package_multi"] = "XercesC"
