from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class ReaderWriterQueue(ConanFile):
    name = "readerwriterqueue"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cameron314/readerwriterqueue"
    description = "A fast single-producer, single-consumer lock-free queue for C++"
    topics = ("cpp11", "cpp14", "cpp17", "queue", "lock-free")
    license = "BSD-2-Clause"
    no_copy_source = True
    settings = "os"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "readerwriterqueue"),
             excludes=["benchmarks", "tests"])

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
