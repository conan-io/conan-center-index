from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class HanaConan(ConanFile):
    name = "hana"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://boostorg.github.io/hana/"
    description = "Hana is a header-only library for C++ metaprogramming suited for computations on both types and values."
    license = "BSL-1.0"
    topics = ("hana", "metaprogramming", "boost")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "_source_subfolder"

    @property
    def _compiler_cpp14_support(self):
        return {
            "gcc": "4.9.3",
            "Visual Studio": "14.0",
            "clang": "3.4",
            "apple-clang": "3.4",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")
        try:
            minimum_required_version = self._compiler_cpp14_support[str(self.settings.compiler)]
            if self.settings.compiler.version < tools.Version(minimum_required_version):
                raise ConanInvalidConfiguration(
                    "This compiler is too old. This library needs a compiler with c++14 support")
        except KeyError:
            self.output.warn("This recipe might not support the compiler. Consider adding it.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced (waiting https://github.com/conan-io/conan/issues/7615 to be implemented)
        self.cpp_info.filenames["cmake_find_package"] = "Hana"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Hana"
        self.cpp_info.names["cmake_find_package"] = "hana"
        self.cpp_info.names["cmake_find_package_multi"] = "hana"
        self.cpp_info.names["pkg_config"] = "hana"
