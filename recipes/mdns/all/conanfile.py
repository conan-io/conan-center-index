import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class MdnsConan(ConanFile):
    name = "mdns"
    description = "Public domain mDNS/DNS-SD library in C"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mjansson/mdns"
    topics = ("dns", "dns-sd", "multicast discovery", "discovery", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        if str(self.settings.os) in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append("pthread")

        self.cpp_info.set_property("cmake_file_name", "mdns")
        self.cpp_info.set_property("cmake_target_name", "mdns::mdns")
