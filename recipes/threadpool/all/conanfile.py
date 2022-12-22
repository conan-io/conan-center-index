from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class ThreadpoolConan(ConanFile):
    name = "threadpool"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/progschj/ThreadPool"
    description = "A simple C++11 Thread Pool implementation."
    license = "Zlib"
    topics = ("c++11", "thread", "pool")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder,  dst=os.path.join(self.package_folder, "include", "ThreadPool"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs.append(os.path.join("include", "ThreadPool"))
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

        # TODO: to remove in conan v2 (and do not port to CMakeDeps, it was a mistake)
        self.cpp_info.names["cmake_find_package"] = "ThreadPool"
        self.cpp_info.names["cmake_find_package_multi"] = "ThreadPool"
