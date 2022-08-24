from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class TaoCPPJSONConan(ConanFile):
    name = "taocpp-json"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/json"
    description = "C++ header-only JSON library"
    topics = ("json", "jaxn", "cbor", "msgpack",
              "ubjson", "json-pointer", "json-patch")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
        }

    @property
    def _min_cppstd_required(self):
        return "11" if tools.scm.Version(self.version) < "1.0.0-beta.11" else "17"

    @property
    def _requires_pegtl(self):
        return tools.scm.Version(self.version) >= "1.0.0-beta.13"

    def requirements(self):
        if self._requires_pegtl:
            self.requires("taocpp-pegtl/3.2.5")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self._min_cppstd_required)
        if tools.scm.Version(self.version) >= "1.0.0-beta.11":
            min_compiler_version = self._min_compilers_version.get(str(self.settings.compiler), False)
            if min_compiler_version:
                if tools.scm.Version(self.settings.compiler.version) < min_compiler_version:
                    raise ConanInvalidConfiguration("taocpp-json requires C++17, which your compiler does not support.")
            else:
                self.output.warn("taocpp-json requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder,
                  strip_root=True)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "taocpp-json")
        self.cpp_info.set_property("cmake_target_name", "taocpp::json")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["json"].bindirs = []
        self.cpp_info.components["json"].frameworkdirs = []
        self.cpp_info.components["json"].libdirs = []
        self.cpp_info.components["json"].resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-json"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-json"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["json"].names["cmake_find_package"] = "json"
        self.cpp_info.components["json"].names["cmake_find_package_multi"] = "json"
        self.cpp_info.components["json"].set_property("cmake_target_name", "taocpp::json")
        if self._requires_pegtl:
            self.cpp_info.components["json"].requires = ["taocpp-pegtl::taocpp-pegtl"]
