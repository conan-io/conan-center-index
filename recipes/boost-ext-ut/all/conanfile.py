from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class UTConan(ConanFile):
    name = "boost-ext-ut"
    description = ("C++17/20 single header/single module, "
                   "macro-free micro Unit Testing Framework")
    topics = ("conan", "UT", "header-only", "unit-test", "tdd", "bdd")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boost-ext.github.io/ut/"
    license = "BSL-1.0"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "9",
            "clang": "9",
            "apple-clang": "11",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ut-" + self.version, self._source_subfolder)
        tools.download("https://www.boost.org/LICENSE_1_0.txt", "LICENSE",
                       sha256="c9bff75738922193e67fa726fa225535870d2aa1059f914"
                       "52c411736284ad566")

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy(os.path.join("include", "boost", "ut.hpp"),
                  src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "boost"
        self.cpp_info.names["cmake_find_package_multi"] = "boost"
        self.cpp_info.filenames["cmake_find_package"] = "ut"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ut"
        self.cpp_info.components["ut"].names["cmake_find_package"] = "ut"
        self.cpp_info.components["ut"].names["cmake_find_package_multi"] = "ut"
