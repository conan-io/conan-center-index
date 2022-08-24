from conan import ConanFile, tools
from conan.tools.cmake import CMake
from fnmatch import fnmatch
import os


class ConcurrentqueueConan(ConanFile):
    name = "concurrentqueue"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cameron314/concurrentqueue"
    description = "A fast multi-producer, multi-consumer lock-free concurrent queue for C++11"
    topics = ("cpp11", "cpp14", "cpp17", "queue", "lock-free")
    license = ["BSD-2-Clause", "BSL-1.0"]
    no_copy_source = True
    settings = "os"
    _source_subfolder = "concurrentqueue"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("concurrentqueue-{}".format(self.version),
                  self._source_subfolder)

    def package(self):
        self.copy("*.h",
                  src=os.path.join(self._source_subfolder),
                  dst=os.path.join("include", "moodycamel"))
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
