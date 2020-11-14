import os
from conans import ConanFile, tools


class AclConan(ConanFile):
    name = "acl"
    description = "Animation Compression Library"
    topics = ("animation", "compression")
    license = "MIT"
    homepage = "https://github.com/nfrechette/acl"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("rtm/2.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "includes"))

    def package_id(self):
        self.info.header_only()
