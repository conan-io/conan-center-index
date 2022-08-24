from conan import ConanFile, tools$

import os

class TclapConan(ConanFile):
    name = "tclap"
    license = "MIT"
    homepage = "http://github.com/xguerin/tclap"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Templatized Command Line Argument Parser"
    topics = ("c++", "commandline parser")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*", src=os.path.join(self._source_subfolder, "include"), dst="include", keep_path=True)

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "tclap"

    def package_id(self):
        self.info.header_only()
