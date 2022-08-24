from conan import ConanFile, tools
from conans import CMake
import os


class SoleConan(ConanFile):
    name = "sole"
    homepage = "https://github.com/r-lyeh-archived/sole"
    description = "Sole is a lightweight C++11 library to generate universally unique identificators (UUID), both v1 and v4."
    topics = ("conan", "uuid", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    no_copy_source = True
    license = "Zlib"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_name = "sole-" + self.version
        os.rename(extracted_name, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include",
                  src=self._source_subfolder)

    def package_info(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("rt")

    def package_id(self):
        self.info.header_only()
