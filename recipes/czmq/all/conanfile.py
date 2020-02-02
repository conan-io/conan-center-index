import os
from conans import ConanFile, tools, CMake


class CZMQConan(ConanFile):
    name = "czmq"
    version = "4.2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/czmq"
    description = "High-level C binding for ØMQ"
    license = "MPL-2.0"
    exports = []
    topics = ("conan", "czmq", "zmq", "zeromq",
              "message-queue", "asynchronous")
    exports_sources = ['CMakeLists.txt', 'patches/*']
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [
        True, False], "lz4": [True, False], "uuid": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True, "lz4": True, "uuid": True}
    generators = ['cmake']
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC
        if self.settings.os == "Macos" and self.options.uuid:
            self.output.warn("czmq doesn't support external libuuid on MacOS")
            self.options.uuid = False
        elif self.settings.os == "Windows" and self.options.uuid:
            self.output.warn(
                "czmq doesn't support external libuuid on Windows")
            self.options.uuid = False

    def build_requirements(self):
        if not tools.which("ninja") and self.settings.compiler == 'Visual Studio':
            self.build_requires.add('ninja/1.9.0')

    def requirements(self):
        self.requires.add('zmq/4.3.2')
        if self.options.lz4:
            self.requires.add('lz4/1.9.2')
        if self.options.uuid:
            self.requires.add('libuuid/1.0.3')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        generator = 'Ninja' if self.settings.compiler == "Visual Studio" else None
        cmake = CMake(self, generator=generator)
        cmake.definitions["CZMQ_BUILD_SHARED"] = self.options.shared
        cmake.definitions["CZMQ_BUILD_STATIC"] = not self.options.shared
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
            self.cpp_info.libs = ['czmq' if self.options.shared else 'libczmq']
            self.cpp_info.libs.append('rpcrt4')
        else:
            self.cpp_info.libs = ['czmq']
            if self.settings.os == "Linux":
                self.cpp_info.libs.extend(["pthread", "m"])
        if not self.options.shared:
            self.cpp_info.defines.append('CZMQ_STATIC')
