import os
from conans import ConanFile, tools

required_conan_version = ">=1.43.0"


class LyraConan(ConanFile):
    name = "lyra"
    homepage = "https://bfgroup.github.io/Lyra/"
    description = "A simple to use, composing, header only, command line arguments parser for C++ 11 and beyond."
    topics = ("cli", "cli-parser", "argparse", "commandline",
              "flags", "header-only", "no-dependencies", "c++11")
    no_copy_source = True
    settings = "compiler"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"

    _source_subfolder = "source_subfolder"

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "lyra")
        self.cpp_info.set_property("cmake_target_name", "bfg::lyra")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_lyra"].set_property("cmake_target_name", "bfg::lyra")
        self.cpp_info.filenames["cmake_find_package"] = "lyra"
        self.cpp_info.filenames["cmake_find_package_multi"] = "lyra"
        self.cpp_info.names["cmake_find_package"] = "bfg"
        self.cpp_info.names["cmake_find_package_multi"] = "bfg"
        self.cpp_info.components["_lyra"].names["cmake_find_package"] = "lyra"
        self.cpp_info.components["_lyra"].names["cmake_find_package_multi"] = "lyra"
