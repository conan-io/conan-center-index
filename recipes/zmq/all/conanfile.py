import os
from conans import ConanFile, tools, CMake


class ZMQConan(ConanFile):
    name = "zmq"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/libzmq"
    description = "ZeroMQ is a community of projects focused on decentralized messaging and computing"
    license = "LGPL-3.0"
    topics = ("conan", "zmq", "libzmq", "message-queue", "asynchronous")
    exports_sources = ['CMakeLists.txt']
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "encryption": [None, "libsodium", "tweetnacl"]}
    default_options = {'shared': False, 'fPIC': True, 'encryption': 'libsodium'}
    generators = ['cmake']
    _source_subfolder = "sources_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.encryption == 'libsodium':
            self.requires.add('libsodium/1.0.18')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libzmq-%s" % self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_CURVE'] = self.options.encryption is not None
        cmake.definitions['WITH_LIBSODIUM'] = self.options.encryption == "libsodium"
        cmake.definitions['ZMQ_BUILD_TESTS'] = False
        cmake.definitions['WITH_PERF_TOOL'] = False
        cmake.definitions['BUILD_SHARED'] = self.options.shared
        cmake.definitions['BUILD_STATIC'] = not self.options.shared
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst='licenses')
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.system_libs = ['ws2_32', 'Iphlpapi']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['pthread', 'rt', 'm'])
        if not self.options.shared:
            self.cpp_info.defines.append('ZMQ_STATIC')

