import os

from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class GraphthewyConan(ConanFile):
    name = "graphthewy"
    license = "EUPL-1.2"
    homepage = "https://github.com/alex-87/graphthewy"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Simple header-only C++ Library for graph modelling (directed or not) and graph cycle detection. "
    topics = ("graph", "algorithm", "modelling", "header-only")
    settings = "compiler"
    no_copy_source = True

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
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

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("graphthewy requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("graphthewy requires C++17, which your compiler does not support.")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst=os.path.join("include", "graphthewy"), src=self._source_subfolder, keep_path=False)

    def package_id(self):
        self.info.header_only()
