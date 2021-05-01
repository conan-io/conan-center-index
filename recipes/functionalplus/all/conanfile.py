from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class FunctionalPlusConan(ConanFile):
    name = "functionalplus"
    description = "Functional Programming Library for C++."
    license = "BSL-1.0"
    topics = ("conan", "functionalplus", "fplus", "functional programming")
    homepage = "https://github.com/Dobiasd/FunctionalPlus"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "4.9",
            "Visual Studio": "14",
            "clang": "3.7",
            "apple-clang": "9",
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("functionalplus requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("functionalplus requires C++14, which your compiler does not support.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("FunctionalPlus-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "FunctionalPlus"
        self.cpp_info.names["cmake_find_package_multi"] = "FunctionalPlus"
        self.cpp_info.components["fplus"].names["cmake_find_package"] = "fplus"
        self.cpp_info.components["fplus"].names["cmake_find_package_multi"] = "fplus"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["fplus"].system_libs = ["pthread"]
