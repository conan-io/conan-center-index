from conan import ConanFile, tools
import glob
import os


class VectorialConan(ConanFile):
    name = "vectorial"
    description = "Vector math library with NEON/SSE support"
    topics = ("conan", "vectorial", "math", "vector")
    license = "BSD-2-Clause"
    homepage = "https://github.com/scoopr/vectorial"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("vectorial-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
