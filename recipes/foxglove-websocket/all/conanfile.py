from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os


class FoxgloveWebSocketConan(ConanFile):
    name = "foxglove-websocket"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/ws-protocol"
    description = "A C++ server implementation of the Foxglove WebSocket Protocol"
    license = "MIT"
    topics = ("foxglove", "websocket")

    settings = ("os", "compiler", "build_type", "arch")
    requires = ("nlohmann_json/3.10.5", "websocketpp/0.8.2")
    generators = ("cmake", "cmake_find_package")

    _source_root = "source_root"
    _source_package_path = os.path.join(_source_root, "cpp", "foxglove-websocket")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_root)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        if (self.settings.compiler == "gcc" or self.settings.compiler == "clang") and tools.Version(self.settings.compiler.version) <= 8:
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) <= "16.8":
            raise ConanInvalidConfiguration("Compiler version is not supported, c++17 support is required")

    def configure(self):
        self.options["websocketpp"].asio = "standalone"

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_package_path)
        self.copy("include/*", src=self._source_package_path)

    def package_id(self):
        self.info.header_only()
