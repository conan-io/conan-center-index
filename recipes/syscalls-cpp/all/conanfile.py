from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.1.0"

class SyscallsCppConan(ConanFile):
    name = "syscalls-cpp"
    description = " A modern C++20 header-only library for advanced direct system call invocation."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sapdragon/syscalls-cpp"
    topics = ("syscall", "windows", "security", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True 

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)
        if self.settings.os != "Windows" or self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.ref} is only supported on Windows x64")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        
    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        
        destination_include_folder = os.path.join(self.package_folder, "include")
        source_include_folder = os.path.join(self.source_folder, "include")
        copy(self, "*.hpp", source_include_folder, destination_include_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_target_name", "sapdragon::syscalls-cpp")
        self.cpp_info.set_property("cmake_target_aliases", ["syscalls-cpp"])
