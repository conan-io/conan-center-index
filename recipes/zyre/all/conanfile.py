from conans import ConanFile, CMake, tools
from sys import platform
import re
import os


class ZyreConan(ConanFile):
    name = "zyre"
    version = "2.0.0"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/zyre"
    description = "Local Area Clustering for Peer-to-Peer Applications."
    topics = ("conan", "zyre", "czmq", "zmq", "zeromq",
              "message-queue", "asynchronous")
    exports_sources = ['CMakeLists.txt']
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False], }
    default_options = {"shared": False,
                       "fPIC": True, }
    generators = ["cmake"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def build_requirements(self):
        if not tools.which("ninja") and \
                self.settings.compiler == 'Visual Studio':
            self.build_requires.add('ninja/1.9.0')

    def requirements(self):
        self.requires.add("zmq/4.3.2")
        self.requires.add("czmq/4.2.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        generator = 'Ninja' if self.settings.compiler == "Visual Studio" \
            else None
        cmake = CMake(self, generator=generator)
        cmake.definitions["ZYRE_BUILD_SHARED"] = self.options.shared
        cmake.definitions["ZYRE_BUILD_STATIC"] = not self.options.shared
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(
            self._source_subfolder, "CMakeLists.txt"), "enable_testing()", '')
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder,
                  dst='licenses')
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs = ['zyre' if self.options.shared else 'libzyre']
        else:
            self.cpp_info.libs = ['zyre']
        if not self.options.shared:
            self.cpp_info.defines.append('ZYRE_STATIC')
