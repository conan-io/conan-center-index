import os

from conan.errors import ConanInvalidConfiguration
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.43.0"

class CSVMONEKYConan(ConanFile):
    name = "csvmonkey"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Header-only vectorized, lazy-decoding, zero-copy CSV file parser "
    topics = ("csv-parser", "header-only", "vectorized")
    homepage = "https://github.com/dw/csvmonkey/"
    settings = "arch", "compiler"
    no_copy_source = True
    options = {"with_spirit": [True, False]}
    default_options = {"with_spirit": False}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.arch not in ("x86", "x86_64",):
            raise ConanInvalidConfiguration("{} requires x86 architecture.".format(self.name))

        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("{} doesn't support Visual Studio C++.".format(self.name))

    def requirements(self):
        if self.options.with_spirit:
            self.requires("boost/1.77.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "csvmonkey")
        self.cpp_info.set_property("cmake_target_name", "csvmonkey::csvmonkey")
        self.cpp_info.set_property("pkg_config_name", "csvmonkey")

        self.cpp_info.filenames["cmake_find_package"] = "csvmonkey"
        self.cpp_info.filenames["cmake_find_package_multi"] = "csvmonkey"
        self.cpp_info.names["cmake_find_package"] = "csvmonkey"
        self.cpp_info.names["cmake_find_package_multi"] = "csvmonkey"

        if self.options.with_spirit:
            self.cpp_info.defines.append("USE_SPIRIT")
