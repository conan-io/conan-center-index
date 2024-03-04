from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class RestinioConan(ConanFile):
    name = "restinio"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/restinio"
    url = "https://github.com/conan-io/conan-center-index"
    description = "RESTinio is a header-only C++17 library that gives you an embedded HTTP/Websocket server."
    topics = ("http-server", "websockets", "rest", "tls-support")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "asio": ["boost", "standalone"],
        "with_openssl": [True, False],
        "with_zlib": [True, False],
        "with_pcre": [1, 2, None],
    }
    default_options = {
        "asio": "standalone",
        "with_openssl": False,
        "with_zlib": False,
        "with_pcre": None,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("llhttp/9.1.3")
        self.requires("fmt/10.2.1")
        self.requires("expected-lite/0.6.3")

        if self.options.asio == "standalone":
            self.requires("asio/1.29.0")
        else:
            self.requires("boost/1.84.0")

        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_pcre == 1:
            self.requires("pcre/8.45")
        elif self.options.with_pcre == 2:
            self.requires("pcre2/10.42")

    def package_id(self):
        self.info.clear()

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "9",
            "clang": "10",
            "apple-clang": "11",
            "Visual Studio": "15",
            "msvc": "191"
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warning(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def build(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.*pp", src=os.path.join(self.source_folder, "dev", "restinio"), dst=os.path.join(self.package_folder, "include", "restinio"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "restinio")
        self.cpp_info.set_property("cmake_target_name", "restinio::restinio")
        if self.options.asio == "boost":
            self.cpp_info.defines.append("RESTINIO_USE_BOOST_ASIO")
