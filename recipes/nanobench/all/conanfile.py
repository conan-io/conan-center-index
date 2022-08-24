import os
import glob
from conan import ConanFile, tools


class NanobenchConan(ConanFile):
    name = "nanobench"
    description = """ankerl::nanobench is a platform independent
                     microbenchmarking library for C++11/14/17/20."""
    topics = ("conan", "nanobench", "benchmark", "microbenchmark")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinus/nanobench"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(
            self._source_subfolder, os.path.join("src", "include"))
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
