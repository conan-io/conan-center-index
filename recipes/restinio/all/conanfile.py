from conans import ConanFile, tools
import os


class RestinioConan(ConanFile):
    name = "restinio"
    license = "BSD-3-CLAUSE"
    homepage = "https://github.com/Stiffstream/restinio"
    url = "https://github.com/conan-io/conan-center-index"
    description = "RESTinio is a header-only C++14 library that gives you an embedded HTTP/Websocket server."
    topics = ("http-server", "websockets", "rest", "tls-support")
    options = {"use_boost": [True, False]}
    default_options = {"use_boost": False}
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "14")

    def requirements(self):
        self.requires("http_parser/2.9.4")
        self.requires("fmt/6.2.1")

        if self.options.use_boost:
            self.requires("boost/1.73.0")
        else:
            self.requires("asio/1.14.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v." + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "dev", "restinio"), dst=os.path.join("include", "restinio"))
        self.copy("*.ipp", src=os.path.join(self._source_subfolder, "dev", "restinio"), dst=os.path.join("include", "restinio"))
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.options.use_boost:
            self.cpp_info.defines.append("RESTINIO_USE_BOOST_ASIO")
