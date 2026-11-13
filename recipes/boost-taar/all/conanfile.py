from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class BoostTaarConan(ConanFile):
    name = "boost-taar"
    description = ("C++20 header-only library for HTTP services on Boost.Asio, "
                   "Boost.Beast, Boost.JSON and Boost.URL: REST, JSON-RPC, MCP "
                   "and OpenAPI")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rjahanbakhshi/boost.taar"
    topics = ("http", "rest", "json-rpc", "mcp", "openapi", "asio", "beast",
              "coroutines", "web-server", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_openssl": [True, False],
    }
    default_options = {
        "with_openssl": True,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        # The oldest compilers the upstream CI covers. GCC 12 lacks
        # <format>.
        return {
            "gcc": "13",
            "clang": "17",
            "apple-clang": "17",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Public headers include Boost and (for TLS) OpenSSL headers.
        self.requires("boost/1.91.0", transitive_headers=True)
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler "
                f"does not fully support (minimum {self.settings.compiler} {minimum_version}).")

        boost = self.dependencies["boost"]
        if boost.options.header_only:
            raise ConanInvalidConfiguration(
                f"{self.ref} needs the compiled Boost.JSON and Boost.URL: "
                "use -o boost/*:header_only=False")
        for component in ("json", "url"):
            if boost.options.get_safe(f"without_{component}"):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires Boost.{component.capitalize()}: "
                    f"use -o boost/*:without_{component}=False")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "boost-taar")
        self.cpp_info.set_property("cmake_target_name", "boost-taar::boost-taar")
        # The name used by add_subdirectory and Boost superproject builds.
        self.cpp_info.set_property("cmake_target_aliases", ["Boost::taar"])
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Boost.System is header-only (in boost::headers).
        self.cpp_info.requires = ["boost::headers", "boost::json", "boost::url"]
        if self.options.with_openssl:
            self.cpp_info.requires.extend(["openssl::ssl", "openssl::crypto"])

        # Mirrors the upstream CMake interface (taar_interface_settings).
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["_WIN32_WINNT=0x0A00", "WIN32_LEAN_AND_MEAN", "NOMINMAX"]
        if is_msvc(self):
            self.cpp_info.cxxflags = ["/bigobj", "/Zc:preprocessor", "/Zc:__cplusplus"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
