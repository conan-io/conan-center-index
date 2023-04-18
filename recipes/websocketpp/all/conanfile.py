from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
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
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/3.1.0", transitive_headers=True, transitive_libs=True)

        if self.options.with_zlib:
            self.requires("zlib/1.2.13", transitive_headers=True, transitive_libs=True)

        if self.options.asio == "standalone":
            self.requires("asio/1.27.0", transitive_headers=True)
        elif self.options.asio == "boost":
            self.requires("boost/1.81.0", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, os.path.join("websocketpp","*.hpp"), src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "websocketpp")
        self.cpp_info.set_property("cmake_target_name", "websocketpp::websocketpp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = []
        if self.options.with_openssl:
            self.cpp_info.requires.append("openssl::openssl")
        if self.options.with_zlib:
            self.cpp_info.requires.append("zlib::zlib")
        if self.options.asio == "standalone":
            self.cpp_info.defines.extend(["ASIO_STANDALONE", "_WEBSOCKETPP_CPP11_STL_"])
            self.cpp_info.requires.append("asio::asio")
        elif self.options.asio == "boost":
            self.cpp_info.requires.append("boost::headers")
