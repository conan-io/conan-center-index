from conans import ConanFile, CMake, tools
import os


class RestinioConan(ConanFile):
    name = "restinio"
    license = "BSD-3-CLAUSE"
    homepage = "https://github.com/Stiffstream/restinio"
    url = "https://github.com/conan-io/conan-center-index"
    description = "RESTinio is a header-only C++14 library that gives you an embedded HTTP/Websocket server."
    topics = ("http-server", "websockets", "rest", "tls-support")
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"use_boost": [True, False], "use_openssl": [True, False]}
    default_options = {"use_boost": False, "use_openssl": False}
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "14")

    def requirements(self):
        self.requires("http_parser/2.9.4")
        self.requires("fmt/6.2.1")
        self.requires("expected-lite/0.4.0")
        self.requires("optional-lite/3.2.0")
        self.requires("string-view-lite/1.3.0")
        self.requires("variant-lite/1.2.2")

        if self.options.use_boost:
            self.requires("boost/1.73.0")
        else:
            self.requires("asio/1.14.1")

        if self.options.use_openssl:
            self.requires("openssl/1.1.1g")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v." + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["RESTINIO_INSTALL"] = True
        self._cmake.definitions["RESTINIO_FIND_DEPS"] = False
        self._cmake.definitions["RESTINIO_FMT_HEADER_ONLY"] = self.options["fmt"].header_only
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_EXPECTED_LITE"] = True
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_OPTIONAL_LITE"] = True
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_STRING_VIEW_LITE"] = True
        self._cmake.definitions["RESTINIO_USE_EXTERNAL_VARIANT_LITE"] = True

        boost_libs = "none"
        if self.options.use_boost:
            if self.options["boost"].shared:
                boost_libs = "shared"
            else:
                boost_libs = "static"
        self._cmake.definitions["RESTINIO_USE_BOOST_ASIO"] = boost_libs

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.defines.extend(["RESTINIO_EXTERNAL_EXPECTED_LITE", "RESTINIO_EXTERNAL_OPTIONAL_LITE",
                                      "RESTINIO_EXTERNAL_STRING_VIEW_LITE", "RESTINIO_EXTERNAL_VARIANT_LITE"])
        if self.options.use_boost:
            self.cpp_info.defines.append("RESTINIO_USE_BOOST_ASIO")
