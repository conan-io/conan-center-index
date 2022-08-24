from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class WebsocketPPConan(ConanFile):
    name = "websocketpp"
    description = "Header only C++ library that implements RFC6455 The WebSocket Protocol"
    topics = ("websocketpp", "websocket", "network", "web", "rfc6455", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zaphoyd/websocketpp"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "asio": ["boost", "standalone", False],
        "with_openssl": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "asio": "boost",
        "with_openssl": True,
        "with_zlib": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1o")

        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

        if self.options.asio == "standalone":
            self.requires("asio/1.22.1")
        elif self.options.asio == "boost":
            self.requires("boost/1.79.0")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        # We have to copy the headers manually, since the upstream cmake.install() step doesn't do so.
        self.copy(pattern=os.path.join("websocketpp","*.hpp"), dst="include", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "websocketpp")
        self.cpp_info.set_property("cmake_target_name", "websocketpp::websocketpp")
        if self.options.asio == "standalone":
            self.cpp_info.defines.extend(["ASIO_STANDALONE", "_WEBSOCKETPP_CPP11_STL_"])
