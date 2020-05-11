from conans import ConanFile, tools
import os


class BitserializerConan(ConanFile):
    name = "bitserializer-pugixml"
    description = "C++ 17 library for serialization, module for support XML (implementation based on the PugiXml library)"
    topics = ("serialization", "xml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/Pavel_Kisliak/bitserializer"
    license = "MIT"
    settings = ("compiler",)
    no_copy_source = True
    requires = ("bitserializer/0.9", "pugixml/1.10@bincrafters/stable")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # Find and rename folder in the extracted sources
        # This workaround used in connection that zip-archive from BitBucket contains folder with some hash in name
        for dirname in os.listdir(self.source_folder):
            if "-bitserializer-" in dirname:
                os.rename(dirname, self._source_subfolder)
                break

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "archives")
        self.copy(pattern="license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="bitserializer_pugixml\\*.h", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
