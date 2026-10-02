from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class TimeShieldCppConan(ConanFile):
    name = "time-shield-cpp"
    description = "Header-only C++ library for time conversions, formatting, and utilities"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LimiNode/time-shield-cpp"
    topics = ("time", "date", "timezone", "ntp", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_ntp": [True, False]}
    default_options = {"with_ntp": True}
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.settings.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TimeShield")
        self.cpp_info.set_property("cmake_target_name", "time_shield::time_shield")
        self.cpp_info.set_property("pkg_config_name", "time-shield")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.defines = [
            "TIME_SHIELD_ENABLE_NTP_CLIENT={}".format(1 if self.options.with_ntp else 0)
        ]
        if self.options.with_ntp and self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
