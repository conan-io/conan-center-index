from conans import ConanFile, tools
import os

class ThrustConan(ConanFile):
    name = "thrust"
    license = "Apache License 2.0"
    description = ("Thrust is a parallel algorithms library which resembles"
                   "the C++ Standard Template Library (STL). Thrust’s high-level "
                   "interface greatly enhances programmer productivity while "
                   "enabling performance portability between GPUs and multicore CPUs."
                   "Interoperability with established technologies "
                   "(such as CUDA, TBB, and OpenMP) facilitates "
                   "integration with existing software.")
    topics = ("conan", "thrust", "parallel", "header_only")
    homepage = "https://thrust.github.io/"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=self._source_subfolder+"/thrust", dst="include/thrust")

    def package_id(self):
        self.info.header_only()
