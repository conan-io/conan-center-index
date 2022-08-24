import os
from conans import ConanFile, tools

class threadpoolConan(ConanFile):
    name = "threadpool"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/progschj/ThreadPool"
    description = "A simple C++11 Thread Pool implementation."
    license = "Zlib"
    topics = ("C++11", "Thread", "Pool", "threadpool", "conan")
    settings = "os", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        listdir = os.listdir()
        extracted_dir = [i for i in listdir if "ThreadPool" in i][0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses", )
        self.copy(pattern="*.h", src=self._source_subfolder,  dst=os.path.join("include", "ThreadPool"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.names["cmake_find_package"] = "ThreadPool"
        self.cpp_info.names["cmake_find_package_multi"] = "ThreadPool"
