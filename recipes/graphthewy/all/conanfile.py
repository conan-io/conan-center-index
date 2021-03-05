import os

from conans import ConanFile, tools


class GraphthewyConan(ConanFile):
    name = "graphthewy"
    version = "1.1"
    license = "EUPL-1.2"
    homepage = "https://github.com/alex-87/graphthewy"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Simple header-only C++ Library for graph modelling (directed or not) and graph cycle detection. "
    topics = ("graph", "algorithm", "modelling", "header-only")
    settings = "os", "compiler"
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10"
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", "include/graphthewy", keep_path=False)

    def package_id(self):
        self.info.header_only()
