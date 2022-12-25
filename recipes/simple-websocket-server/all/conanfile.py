import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class SimpleWebSocketServerConan(ConanFile):
    name = "simple-websocket-server"
    homepage = "https://gitlab.com/eidheim/Simple-WebSocket-Server"
    description = "A very simple, fast, multithreaded, platform independent WebSocket (WS) and WebSocket Secure (WSS) server and client library."
    topics = ("websocket", "socket", "server", "client", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True
    license = "MIT"
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
        self.requires("openssl/1.1.1q")
        # only version 2.0.2 upwards is able to build against asio 1.18.0 or higher
        if tools.Version(self.version) <= "2.0.1":
            if self.options.use_asio_standalone:
                self.requires("asio/1.16.1")
            else:
                self.requires("boost/1.73.0")
        else:
            if self.options.use_asio_standalone:
                self.requires("asio/1.23.0")
            else:
                self.requires("boost/1.79.0")

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def build(self):
        if tools.Version(self.version) <= "2.0.1" and "asio" in self.deps_cpp_info.deps and tools.Version(self.deps_cpp_info["asio"].version) >= "1.18.0":
            raise ConanInvalidConfiguration("simple-websocket-server versions <=2.0.1 require asio < 1.18.0")
        elif tools.Version(self.version) <= "2.0.1" and "boost" in self.deps_cpp_info.deps and tools.Version(self.deps_cpp_info["boost"].version) >= "1.74.0":
            raise ConanInvalidConfiguration("simple-websocket-server versions <=2.0.1 require boost < 1.74.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Simple-WebSocket-Server-v" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst=os.path.join("include", "simple-websocket-server"), src=self._source_subfolder)

    def package_info(self):
        if self.options.use_asio_standalone:
            self.cpp_info.defines.append('USE_STANDALONE_ASIO')

    def package_id(self):
        self.info.header_only()
