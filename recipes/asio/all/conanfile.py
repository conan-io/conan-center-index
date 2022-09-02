from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class Asio(ConanFile):
    name = "asio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://think-async.com/Asio"
    description = "Asio is a cross-platform C++ library for network and low-level I/O"
    topics = ("asio", "network", "io", "low-level")
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        root_dir = os.path.join(self.source_folder, "asio")
        include_dir = os.path.join(root_dir, "include")
        copy(self, "LICENSE_1_0.txt", src=root_dir, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=include_dir, dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.ipp", src=include_dir, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.defines.append("ASIO_STANDALONE")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
