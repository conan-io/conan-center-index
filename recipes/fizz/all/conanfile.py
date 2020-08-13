from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class FizzConan(ConanFile):
    name = "fizz"
    description = " Fizz, a robust, highly performant TLS library written in C++ 14. In addition to the protocol enhancements that come with TLS 1.3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookincubator/fizz"
    topics = ("conan", "tls", "networking", "client", "server")
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

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
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("fizz not be built by Visual Studio due to it's dependencies.") # libiberty
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.73.0")
        self.requires("libevent/2.1.12")
        self.requires("double-conversion/3.1.5")
        self.requires("glog/0.4.0")
        self.requires("gflags/2.2.2")
        self.requires("libiberty/9.1.0")
        self.requires("lz4/1.9.2")
        self.requires("lzma_sdk/9.20")
        self.requires("snappy/1.1.7")
        # zlib1g
        self.requires("jemalloc/5.2.1")
        self.requires("openssl/1.1.1g")
        self.requires("libsodium/1.0.18")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
