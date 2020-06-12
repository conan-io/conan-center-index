from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from glob import glob
import os


class NngConan(ConanFile):
    name = "nng"
    description = "nanomsg-next-generation: light-weight brokerless messaging"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "src/*.cmake", "src/*.txt"]
    homepage = "https://github.com/nanomsg/nng"
    license = "MIT"
    topics = ("nanomsg", "communication", "messaging", "protocols")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tests": [True, False],
        "nngcat": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tests": False,
        "nngcat": False
    }

    _source_subfolder = "source_subfolder"
    _cmake = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.compiler == "Visual Studio" and \
                tools.Version(self.settings.compiler.version) < 14:
            raise ConanInvalidConfiguration("MSVC < 14 is not supported")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["NNG_TESTS"] = self.options.tests
        self._cmake.definitions["NNG_NNGCAT"] = self.options.nngcat
        self._cmake.configure(source_folder=self._source_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt",
                  dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.libs.extend(['mswsock', 'ws2_32'])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(['pthread'])

        if not self.options.shared:
            self.cpp_info.defines.append("NN_STATIC_LIB=ON")

        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "nng")]
