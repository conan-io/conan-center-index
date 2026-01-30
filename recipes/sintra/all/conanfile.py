from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class SintraConan(ConanFile):
    name = "sintra"
    version = "1.0.2"
    license = "BSD-2-Clause"
    homepage = "https://github.com/imakris/sintra"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Header-only C++17 IPC library using shared-memory ring buffers."
    topics = ("ipc", "shared-memory", "rpc", "pubsub", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self)

    def validate(self):
        check_min_cppstd(self, 17)
        allowed_architectures = {"x86", "x86_64", "armv7", "armv8"}
        if str(self.settings.arch) not in allowed_architectures:
            raise ConanInvalidConfiguration(
                "sintra supports x86, x86_64, armv7, and armv8 architectures")
        allowed_os = {"Windows", "Linux", "Macos", "FreeBSD"}
        if str(self.settings.os) not in allowed_os:
            raise ConanInvalidConfiguration(
                "sintra supports Windows, Linux, macOS, and FreeBSD")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            "*",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"))
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "sintra")
        self.cpp_info.set_property("cmake_target_name", "sintra::sintra")
