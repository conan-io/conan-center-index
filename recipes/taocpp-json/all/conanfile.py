import os
from conans import ConanFile, tools
from conans.tools import Version
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

    def _has_support_for_cpp17(self):
        supported_compilers = [
            ("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(
            self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("Taocpp JSON requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

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
