import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"

class TaoCPPPEGTLConan(ConanFile):
    name = "taocpp-pegtl"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/pegtl"
    description = "Parsing Expression Grammar Template Library"
    topics = ("peg", "header-only", "cpp",
              "parsing", "cpp17", "cpp11", "grammar")
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "15.7",
            "clang": "6",
            "apple-clang": "10",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("TaoCPP PEGTL requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("TaoCPP PEGTL requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "PEGTL-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "pegtl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pegtl"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package"] = "pegtl"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package_multi"] = "pegtl"
