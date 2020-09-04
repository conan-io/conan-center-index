import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"

class TaoCPPJSONConan(ConanFile):
    name = "taocpp-json"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/json"
    description = "C++ header-only JSON library"
    topics = ("json", "jaxn", "cbor", "msgpack",
              "ubjson", "json-pointer", "json-patch")
    settings = "compiler"
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

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")
        min_compiler_version = self._min_compilers_version.get(str(self.settings.compiler), False)
        if min_compiler_version:
            if tools.Version(self.settings.compiler.version) < min_compiler_version:
                raise ConanInvalidConfiguration("taocpp-json requires C++17, which your compiler does not support.")
        else:
            self.output.warn("taocpp-json requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "json-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-json"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-json"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-json"].names["cmake_find_package"] = "json"
        self.cpp_info.components["_taocpp-json"].names["cmake_find_package_multi"] = "json"
