import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class ZmqppConan(ConanFile):
    name = "zmqpp"
    homepage = "https://github.com/zeromq/zmqpp"
    version = "4.2.0"
    version_major = 4
    license = "MPLv2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "This C++ binding for 0mq/zmq is a 'high-level' library that hides most of the c-style interface core 0mq provides."
    topics = ("conan", "zmq", "0mq", "ZeroMQ", "message-queue", "asynchronous")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        self.requires("libsodium/1.0.18")
        self.requires("zeromq/4.3.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zmqpp-%s" % (self.version), self._source_subfolder)

    def validate(self):
        compiler = self.settings.compiler
        if compiler.get_safe('cppstd'):
            tools.check_min_cppstd(self, 11)

        # libstdc++11 is required
        #if self.settings.compiler == "Visual Studio":
        #    raise ConanInvalidConfiguration("Visual Studio compiler is not supported")
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")
        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")

    def build(self):
        self.cmake = CMake(self)
        self.cmake.configure()
        self.cmake.build()

    def package(self):
        self.cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["zmqpp"]
