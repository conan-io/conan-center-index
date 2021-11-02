import os
from conans import ConanFile, tools
import conan.tools.files

class WebsocketPPConan(ConanFile):
    name = "websocketpp"
    description = "Header only C++ library that implements RFC6455 The WebSocket Protocol"
    topics = ("websocketpp", "websocket", "network", "web", "rfc6455", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zaphoyd/websocketpp"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/*"]
    options = {"asio": ["boost", "standalone", "none"],
               "openssl": [True, False],
               "zlib": [True, False]}
    default_options = {"asio": "boost", "openssl": True, "zlib": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.openssl:
            self.requires("openssl/1.1.1k")

        if self.options.zlib:
            self.requires("zlib/1.2.11")

        if self.options.asio == "standalone":
            self.requires("asio/1.19.2")
        elif self.options.asio == "boost":
            self.requires("boost/1.76.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        conan.tools.files.rename(self, src = extracted_dir, dst = self._source_subfolder)

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
