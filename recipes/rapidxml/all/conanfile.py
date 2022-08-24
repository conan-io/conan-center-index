import os

from conan import ConanFile, tools

class RapiXMLConan(ConanFile):
    name = "rapidxml"
    description = "RapidXml is an attempt to create the fastest XML parser possible."
    license = ["BSL-1.0", "MIT"]
    topics = ("conan", "rapidxml", "xml", "parser")
    homepage = "http://rapidxml.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy(pattern="license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst=os.path.join("include", "rapidxml"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "rapidxml"))
