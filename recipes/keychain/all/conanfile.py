from conan import ConanFile, tools
from conans import CMake
import os

class KeychainConan(ConanFile):
    name = "keychain"
    homepage = "https://github.com/hrantzsch/keychain"
    description = "A cross-platform wrapper for the operating system's credential storage"
    topics = ("conan", "keychain", "security", "credentials", "password", "cpp11")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "pkg_config"
    options = {'fPIC': [False, True]}
    default_options = {'fPIC': True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
     if self.settings.compiler.cppstd:
         tools.check_min_cppstd(self, 11)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libsecret/0.20.4")

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ['Security', 'CoreFoundation']
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ['crypt32']
