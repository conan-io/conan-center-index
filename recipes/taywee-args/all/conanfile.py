from conans import ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class TayweeArgsConan(ConanFile):
    name = "taywee-args"
    description = "A simple, small, flexible, single-header C++11 argument parsing library"
    topics = ("conan", "taywee-args", "args", "argument-parser", "header-only")
    license = "MIT"
    homepage = "https://github.com/Taywee/args"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("args-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("args.hxx", dst="include", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "args"
        self.cpp_info.filenames["cmake_find_package_multi"] = "args"
        self.cpp_info.names["cmake_find_package"] = "taywee"
        self.cpp_info.names["cmake_find_package_multi"] = "taywee"
        self.cpp_info.components["libargs"].names["cmake_find_package"] = "args"
        self.cpp_info.components["libargs"].names["cmake_find_package_multi"] = "args"
