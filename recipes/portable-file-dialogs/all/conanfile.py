import os
from conans import ConanFile, tools


class PortableFileDialogsConan(ConanFile):
    name = "portable-file-dialogs"
    license = "WTFPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/samhocevar/portable-file-dialogs"
    description = "Portable GUI dialogs library, C++11, single-header"
    topics = ("conan", "gui", "dialogs")
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("portable-file-dialogs.h", dst="include", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.libdirs = []
