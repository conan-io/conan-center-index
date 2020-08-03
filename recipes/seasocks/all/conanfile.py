from conans import ConanFile, CMake, tools
import os


class SeasocksConan(ConanFile):
    name = "seasocks"
    description = "Simple, small, C++ embeddable webserver with WebSockets support"
    topics = ("conan", "seasocks", "websockets", "http")
    license = 'BSD 2-clause "Simplified" License'
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mattgodbolt/seasocks"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "support_deflate": [True, False]}
    default_options = {"shared": True, "support_deflate": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.support_deflate:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("seasocks-" + self.version, self._source_subfolder)

    def _config_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DEFLATE_SUPPORT"] = "ON" if self.options.support_deflate else "OFF"
        self._cmake.definitions["SEASOCKS_EXAMPLE_APP"] = "OFF"
        self._cmake.definitions["UNITTESTS"] = "OFF"
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._config_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._config_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'CMake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
