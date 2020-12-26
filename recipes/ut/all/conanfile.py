from conans import ConanFile, CMake, tools
import os
import glob


class UTConan(ConanFile):
    name = "ut"
    description = "C++20 single header/single module, macro-free micro Unit Testing Framework"
    topics = ("conan", "UT", "header-only", "unit-test", "tdd", "bdd")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boost-ext.github.io/ut/"
    license = "Boost"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ut-" + self.version, self._source_subfolder)
        tools.download("https://www.boost.org/LICENSE_1_0.txt", "LICENSE", sha256="c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566")

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy(os.path.join("include", "boost", "ut.hpp"), dst=os.path.join("include", "boost"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "UT"
        self.cpp_info.names["cmake_find_package_multi"] = "UT"
        self.cpp_info.includedirs.append(os.path.join("include", "boost"))
