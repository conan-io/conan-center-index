from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class SintraConan(ConanFile):
    name = "sintra"
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
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
