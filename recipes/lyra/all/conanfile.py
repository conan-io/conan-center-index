from conans import ConanFile, tools
import os

required_conan_version = ">=1.28.0"

class LyraConan(ConanFile):
    name = "lyra"
    homepage = "https://bfgroup.github.io/Lyra/"
    description = "A simple to use, composing, header only, command line arguments parser for C++ 11 and beyond."
    topics = ("conan", "cli", "c++11")
    no_copy_source = True
    settings = "compiler"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Lyra-" + \
            os.path.basename(self.conan_data["sources"][self.version]['url']).replace(
                ".tar.gz", "")
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "lyra"
        self.cpp_info.filenames["cmake_find_package_multi"] = "lyra"
        self.cpp_info.names["cmake_find_package"] = "bfg"
        self.cpp_info.names["cmake_find_package_multi"] = "bfg"
        self.cpp_info.components["_lyra"].names["cmake_find_package"] = "lyra"
        self.cpp_info.components["_lyra"].names["cmake_find_package_multi"] = "lyra"
