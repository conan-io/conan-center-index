from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class NngConan(ConanFile):
    name = "nng"
    description = "nanomsg-next-generation: light-weight brokerless messaging"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    homepage = "https://github.com/nanomsg/nng"
    license = "MIT"
    topics = ("nanomsg", "communication", "messaging", "protocols")
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "nngcat": [True, False],
        "http": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "nngcat": False,
        "http": True,
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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.compiler == "Visual Studio" and \
                tools.Version(self.settings.compiler.version) < 14:
            raise ConanInvalidConfiguration("MSVC < 14 is not supported")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["NNG_TESTS"] = False
        self._cmake.definitions["NNG_ENABLE_TLS"] = False
        self._cmake.definitions["NNG_ENABLE_NNGCAT"] = self.options.nngcat
        self._cmake.definitions["NNG_ENABLE_HTTP"] = self.options.http
        self._cmake.configure()

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.extend(['mswsock', 'ws2_32'])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(['pthread'])

        if self.options.shared:
            self.cpp_info.defines.append("NNG_SHARED_LIB")
        else:
            self.cpp_info.defines.append("NNG_STATIC_LIB")
