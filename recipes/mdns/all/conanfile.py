import os
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.43.0"

class MdnsConan(ConanFile):
    name = "mdns"
    license = "Unlicense"
    homepage = "https://github.com/mjansson/mdns"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Public domain mDNS/DNS-SD library in C"
    topics = ("mdns", "dns", "dns-sd", "multicast discovery", "discovery")
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        if str(self.settings.os) in ["Linux", "Android"]:
            self.cpp_info.system_libs.append('pthread')

        self.cpp_info.set_property("cmake_file_name", "mdns")
        self.cpp_info.set_property("cmake_target_name", "mdns::mdns")
