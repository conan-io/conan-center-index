import os

from conans import ConanFile, tools


class SimpleWebSocketServerConan(ConanFile):
    name = "simple-websocket-server"
    homepage = "https://gitlab.com/eidheim/Simple-WebSocket-Server"
    description = "A very simple, fast, multithreaded, platform independent WebSocket (WS) and WebSocket Secure (WSS) server and client library."
    topics = ("websocket", "socket", "server", "client", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True
    license = "MIT"
    requires = (
        "openssl/1.1.1d",
    )
    options = {
        "use_asio_standalone": [True, False],
    }
    default_options = {
        "use_asio_standalone": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.use_asio_standalone:
            self.requires("asio/1.13.0")
        else:
            self.requires("boost/1.71.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Simple-WebSocket-Server-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include/simple-websocket-server", src=self._source_subfolder)

    def package_info(self):
        if self.options.use_asio_standalone:
            self.cpp_info.defines.append('USE_STANDALONE_ASIO')

    def package_id(self):
        self.info.header_only()
