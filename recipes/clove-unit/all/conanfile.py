from conan import ConanFile, tools$

required_conan_version = ">=1.43.0"

class CloveUnitConan(ConanFile):
    name = "clove-unit"
    description = "Single-header Unit Testing framework for C (interoperable with C++) with test autodiscovery feature"
    topics = ("clove-unit", "unit-testing", "testing", "unit testing", "test")
    homepage = "https://github.com/fdefelici/clove-unit"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="clove-unit.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CloveUnit"
        self.cpp_info.names["cmake_find_package_multi"] = "CloveUnit"
