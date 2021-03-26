import os, glob
from conans import CMake, ConanFile, tools


class MdnsConan(ConanFile):
    name = "mdns"
    license = "Unlicense"
    homepage = "https://github.com/mjansson/mdns"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Public domain mDNS/DNS-SD library in C"
    topics = ("conan", "mdns", "dns", "dns-sd")
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('mdns-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        if str(self.settings.os) in ["Linux", "Android"]:
            self.cpp_info.system_libs.append('pthread')

    def package_id(self):
        self.info.header_only()
