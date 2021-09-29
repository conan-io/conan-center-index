from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class RestinioConan(ConanFile):
    name = "restinio"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/restinio"
    url = "https://github.com/conan-io/conan-center-index"
    description = "RESTinio is a header-only C++14 library that gives you an embedded HTTP/Websocket server."
    topics = ("http-server", "websockets", "rest", "tls-support")
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"asio": ["boost", "standalone"], "with_openssl": [True, False], "with_zlib": [True, False], "with_pcre": [1, 2, None]}
    default_options = {"asio": "standalone", "with_openssl": False, "with_zlib": False, "with_pcre": None}
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
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

    def requirements(self):
        self.requires("http_parser/2.9.4")
        self.requires("fmt/8.0.1")
        self.requires("expected-lite/0.5.0")
        self.requires("optional-lite/3.4.0")
        self.requires("string-view-lite/1.6.0")
        self.requires("variant-lite/2.0.0")

        if self.options.asio == "standalone":
            if tools.Version(self.version) >= "0.6.9":
                self.requires("asio/1.18.1")
            else:
                self.requires("asio/1.16.1")
        else:
            if tools.Version(self.version) >= "0.6.9":
                self.requires("boost/1.77.0")
            else:
                self.requires("boost/1.73.0")

        if self.options.with_openssl:
            self.requires("openssl/1.1.1l")

        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

        if self.options.with_pcre == 1:
            self.requires("pcre/8.45")
        elif self.options.with_pcre == 2:
            self.requires("pcre2/10.37")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["RESTINIO_INSTALL"] = True
        self._cmake.definitions["RESTINIO_FIND_DEPS"] = False
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_EXPECTED_LITE"] = True
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_OPTIONAL_LITE"] = True
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_STRING_VIEW_LITE"] = True
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_VARIANT_LITE"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.defines.extend(["RESTINIO_EXTERNAL_EXPECTED_LITE", "RESTINIO_EXTERNAL_OPTIONAL_LITE",
                                      "RESTINIO_EXTERNAL_STRING_VIEW_LITE", "RESTINIO_EXTERNAL_VARIANT_LITE"])
        if self.options.asio == "boost":
            self.cpp_info.defines.append("RESTINIO_USE_BOOST_ASIO")
