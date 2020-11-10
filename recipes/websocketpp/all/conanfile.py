import os
from conans import ConanFile, tools


class WebsocketPPConan(ConanFile):
    name = "websocketpp"
    description = "Header only C++ library that implements RFC6455 The WebSocket Protocol"
    topics = ("conan", "websocketpp", "websocket", "network", "web", "rfc6455", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zaphoyd/websocketpp"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/*"]
    options = {"asio": ["boost", "standalone"]}
    default_options = {"asio": "boost"}
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("openssl/1.1.1h")
        self.requires("zlib/1.2.11")
        if self.options.asio == "standalone":
            self.requires("asio/1.16.1")
        else:
            self.requires("boost/1.74.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        # We have to copy the headers manually, since the upstream cmake.install() step doesn't do so.
        self.copy(pattern=os.path.join("websocketpp","*.hpp"), dst="include", src=self._source_subfolder)

    def package_info(self):
        if self.options.asio == "standalone":
            self.cpp_info.defines.extend(["ASIO_STANDALONE", "_WEBSOCKETPP_CPP11_STL_"])

    def package_id(self):
        self.info.header_only()
