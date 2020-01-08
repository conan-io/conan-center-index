import os
from conans import ConanFile, CMake, tools


class EABaseConan(ConanFile):
    name = "eabase"
    description = "EABase is a small set of header files that define platform-independent data types and platform feature macros. "
    topics = ("conan", "eabase", "config",)
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EABase"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        folder_name = "EABase-{}".format(self.version)
        os.rename(folder_name, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "EABase"
        self.cpp_info.names["cmake_find_package_multi"] = "EABase"
        self.cpp_info.includedirs.extend([os.path.join("include", "Common"),
                                          os.path.join("include", "Common", "EABase")])
