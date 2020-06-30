import os

from conans import ConanFile, tools


class UwebsocketsConan(ConanFile):
    name = "uwebsockets"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Simple, secure & standards compliant web server for the most demanding of applications"
    license = "Apache-2.0"
    homepage = "https://github.com/uNetworking/uWebSockets"
    topics = ("conan", "websocket", "network")
    no_copy_source = True

    requires = ("usockets/0.4.0",
                "zlib/1.2.11")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("uWebSockets-%s" % self.version, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "src"), dst="include/uWebSockets", keep_path=False)
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "src", "f2"), dst="include/uWebSockets/f2", keep_path=False)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "uWebSockets"))
