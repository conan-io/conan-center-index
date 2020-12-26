from conans import ConanFile, CMake, tools
import os
import glob


class UTConan(ConanFile):
    name = "ut"
    description = "C++20 single header/single module, "
    "macro-free micro Unit Testing Framework"
    topics = ("conan", "UT", "header-only", "unit-test", "tdd", "bdd")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boost-ext.github.io/ut/"
    license = "Boost"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True

    def configure(self):
        self._validate_compiler_settings()

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        self.cpp_info.names["cmake_find_package"] = "UT"
        self.cpp_info.names["cmake_find_package_multi"] = "UT"

    def _validate_compiler_settings(self):
        tools.check_min_cppstd(self, "20")
        self._require_at_least_compiler_version("apple-clang", 11)
        self._require_at_least_compiler_version("clang", 9)
        self._require_at_least_compiler_version("gcc", 9)
        self._require_at_least_compiler_version("Visual Studio", 16)

    def _require_at_least_compiler_version(self, compiler, compiler_version):
        if self.settings.compiler == compiler \
                and tools.Version(self.settings.compiler.version) \
                < compiler_version:
            raise ConanInvalidConfiguration(
                "{}/{} with compiler {} requires at least compiler version {}".
                format(self.name, self.version, compiler, compiler_version))
