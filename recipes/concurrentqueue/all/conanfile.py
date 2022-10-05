from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class ConcurrentqueueConan(ConanFile):
    name = "concurrentqueue"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cameron314/concurrentqueue"
    description = "A fast multi-producer, multi-consumer lock-free concurrent queue for C++11"
    topics = ("cpp11", "cpp14", "cpp17", "queue", "lock-free")
    license = ["BSD-2-Clause", "BSL-1.0"]
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        for file in ["blockingconcurrentqueue.h", "concurrentqueue.h", "lightweightsemaphore.h"]:
            copy(self, file, src=self.source_folder, dst=os.path.join(self.package_folder, "include", "moodycamel"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "concurrentqueue")
        self.cpp_info.set_property("cmake_target_name", "concurrentqueue::concurrentqueue")
        self.cpp_info.includedirs.append(os.path.join("include", "moodycamel"))
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
