from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class SeasocksConan(ConanFile):
    name = "seasocks"
    description = "A tiny embeddable C++ HTTP and WebSocket server for Linux"
    topics = ("seasocks", "embeddable", "webserver", "websockets")
    homepage = "https://github.com/mattgodbolt/seasocks"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Seasocks doesn't support this os")
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("seasocks-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DEFLATE_SUPPORT"] = self.options.with_zlib
        self._cmake.definitions["SEASOCKS_SHARED"] = self.options.shared
        self._cmake.definitions["SEASOCKS_EXAMPLE_APP"] = False
        self._cmake.definitions["UNITTESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # Set the name of the generated `FindSeasocks.cmake` and
        # `SeasocksConfig.cmake` cmake scripts
        self.cpp_info.names["cmake_find_package"] = "Seasocks"
        self.cpp_info.names["cmake_find_package_multi"] = "Seasocks"
        self.cpp_info.components["libseasocks"].libs = ["seasocks"]
        self.cpp_info.components["libseasocks"].system_libs = ["pthread"]
        # Set the name of the generated seasocks target: `Seasocks::seasocks`
        self.cpp_info.components["libseasocks"].names["cmake_find_package"] = "seasocks"
        self.cpp_info.components["libseasocks"].names["cmake_find_package_multi"] = "seasocks"
        if self.options.with_zlib:
            self.cpp_info.components["libseasocks"].requires = ["zlib::zlib"]
