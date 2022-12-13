from conan import ConanFile
from conan.tools import files
import os

required_conan_version = ">=1.52.0"


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

    def export_sources(self):
        files.export_conandata_patches(self)

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1s")

        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

        if self.options.asio == "standalone":
            self.requires("asio/1.24.0")
        elif self.options.asio == "boost":
            self.requires("boost/1.80.0")

    def package_id(self):
        self.info.header_only()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def build(self):
        files.apply_conandata_patches(self)

    def package(self):
        files.copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        # We have to copy the headers manually, since the upstream cmake.install() step doesn't do so.
        files.copy(self, pattern=os.path.join("websocketpp","*.hpp"), dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "websocketpp")
        self.cpp_info.set_property("cmake_target_name", "websocketpp::websocketpp")
        if self.options.asio == "standalone":
            self.cpp_info.defines.extend(["ASIO_STANDALONE", "_WEBSOCKETPP_CPP11_STL_"])
