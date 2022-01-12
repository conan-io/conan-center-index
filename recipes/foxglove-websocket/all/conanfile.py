from conans import ConanFile, CMake, tools
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
    generators = "cmake"

    _source_root = "source_root"
    _source_package_path = os.path.join(_source_root, "cpp", "foxglove-websocket")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_root)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

    def configure(self):
        self.options["websocketpp"].asio = "standalone"

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_package_path)
        self.copy("include/*", src=self._source_package_path)

    def package_id(self):
        self.info.header_only()
