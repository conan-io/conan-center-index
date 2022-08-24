from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class RestinioConan(ConanFile):
    name = "restinio"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/restinio"
    url = "https://github.com/conan-io/conan-center-index"
    description = "RESTinio is a header-only C++14 library that gives you an embedded HTTP/Websocket server."
    topics = ("http-server", "websockets", "rest", "tls-support")

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

    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("http_parser/2.9.4")

        if tools.Version(self.version) >= "0.6.16":
            self.requires("fmt/9.0.0")
        else:
            self.requires("fmt/8.1.1")

        self.requires("expected-lite/0.5.0")
        self.requires("optional-lite/3.5.0")
        self.requires("string-view-lite/1.6.0")
        self.requires("variant-lite/2.0.0")

        if self.options.asio == "standalone":
            if tools.Version(self.version) >= "0.6.9":
                self.requires("asio/1.22.1")
            else:
                self.requires("asio/1.16.1")
        else:
            if tools.Version(self.version) >= "0.6.9":
                self.requires("boost/1.78.0")
            else:
                self.requires("boost/1.73.0")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1n")

        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

        if self.options.with_pcre == 1:
            self.requires("pcre/8.45")
        elif self.options.with_pcre == 2:
            self.requires("pcre2/10.40")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "15"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RESTINIO_INSTALL"] = True
        cmake.definitions["RESTINIO_FIND_DEPS"] = False
        cmake.definitions["RESTINIO_USE_EXTERNAL_EXPECTED_LITE"] = True
        cmake.definitions["RESTINIO_USE_EXTERNAL_OPTIONAL_LITE"] = True
        cmake.definitions["RESTINIO_USE_EXTERNAL_STRING_VIEW_LITE"] = True
        cmake.definitions["RESTINIO_USE_EXTERNAL_VARIANT_LITE"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "restinio")
        self.cpp_info.set_property("cmake_target_name", "restinio::restinio")
        self.cpp_info.defines.extend(["RESTINIO_EXTERNAL_EXPECTED_LITE", "RESTINIO_EXTERNAL_OPTIONAL_LITE",
                                      "RESTINIO_EXTERNAL_STRING_VIEW_LITE", "RESTINIO_EXTERNAL_VARIANT_LITE"])
        if self.options.asio == "boost":
            self.cpp_info.defines.append("RESTINIO_USE_BOOST_ASIO")
