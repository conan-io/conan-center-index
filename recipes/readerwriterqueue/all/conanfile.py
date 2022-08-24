from conans import ConanFile, tools
import os


class ReaderWriterQueue(ConanFile):
    name = "readerwriterqueue"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cameron314/readerwriterqueue"
    description = "A fast single-producer, single-consumer lock-free queue for C++"
    topics = ("cpp11", "cpp14", "cpp17", "queue", "lock-free")
    license = "BSD-2-Clause"
    no_copy_source = True
    settings = "os"
    
    @property
    def _source_subfolder(self):
        return "sources_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("readerwriterqueue-{}".format(self.version),
                  self._source_subfolder)

    def package(self):
        self.copy("atomicops.h", src=self._source_subfolder, dst=os.path.join("include", "readerwriterqueue"))
        self.copy("readerwriterqueue.h", src=self._source_subfolder, dst=os.path.join("include", "readerwriterqueue"))
        if tools.scm.Version(self, self.version) >= "1.0.5":
            self.copy("readerwritercircularbuffer.h", src=self._source_subfolder, dst=os.path.join("include", "readerwriterqueue"))

        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
