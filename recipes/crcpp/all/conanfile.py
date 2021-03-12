from conans import ConanFile, tools
import os


class CrcppConan(ConanFile):
    name = "crcpp"
    version = "1.0.1.0"
    license = "BSD"
    url = "https://github.com/d-bahr/CRCpp"
    description = "Easy to use and fast C++ CRC library."
    topics = ("CRC")
    settings = "os"

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("CRCpp-release-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("CRC.h", src=os.path.join(self._source_subfolder, "inc"), dst=os.path.join("include", "crcpp"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "crcpp"))

    def package_id(self):
        self.info.header_only()
