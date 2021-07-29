from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class CsvParserConan(ConanFile):
    name = "csv-parser"
    description = "Vince's CSV Parser with simple and intuitive syntax"
    topics = ("conan", "csv-parser", "csv", "rfc 4180", "parser", "generator")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vincentlaucsb/csv-parser"
    license = "MIT"
    settings = "os", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _supports_cpp11(self):
        supported_compilers = [("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = tools.Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def validate(self):
        tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "single_include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CSVParser"
        self.cpp_info.names["cmake_find_package_multi"] = "CSVParser"

        if self.settings.os == "Linux" or self.settings.os == "FreeBSD":
            self.cpp_info.system_libs.append("pthread")
