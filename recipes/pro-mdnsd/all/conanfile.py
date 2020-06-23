import os
import sys
from conans import ConanFile, CMake, tools
from conans.tools import download, unzip
from conans.model.version import Version


class mdnsdConan(ConanFile):
    name = "pro-mdnsd"
    license = "BSD 3-Clause"
    exports_sources = [
        "CMakeLists.txt",
        "patches/**"
    ]
    homepage = "https://github.com/Pro/mdnsd"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Improved version of Jeremie Miller's MDNS-SD implementation"
    topics = ("dns", "daemon", "multicast", "embedded", "c")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "cpp_compatible": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "cpp_compatible": False
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if not self.options.cpp_compatible:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        if Version(self.version) <= "0.8.0":
            folder_name = "%s-%s" % ("mdnsd", "0.8")
        else:
            folder_name = "%s-%s" % (self.name, self.version)
        os.rename(folder_name, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.verbose = True
        self._cmake.definitions["MDNSD_COMPILE_AS_CXX"] = self.options.cpp_compatible
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "mdnsd"
        self.cpp_info.libs = ["libmdnsd"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
