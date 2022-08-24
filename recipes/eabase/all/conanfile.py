import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake


class EABaseConan(ConanFile):
    name = "eabase"
    description = "EABase is a small set of header files that define platform-independent data types and platform feature macros. "
    topics = ("conan", "eabase", "config",)
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EABase"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "EABase-{}".format(self.version)
        os.rename(folder_name, self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "EABase"
        self.cpp_info.names["cmake_find_package_multi"] = "EABase"
        self.cpp_info.includedirs.extend([os.path.join("include", "Common"),
                                          os.path.join("include", "Common", "EABase")])
