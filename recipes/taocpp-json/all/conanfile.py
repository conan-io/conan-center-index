import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.error import ConanInvalidConfiguration


class TaoCPPJSONConan(ConanFile):
    name = "taocpp-json"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/json"
    description = "C++ header-only JSON library"
    topics = ("json", "jaxn", "cbor", "msgpack", "ubjson", "json-pointer", "json-patch")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("Taocpp JSON requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "json-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.definitions["TAOCPP_JSON_BUILD_TESTS"] = False
        cmake.definitions["TAOCPP_JSON_BUILD_EXAMPLES"] = False
        cmake.definitions["TAOCPP_JSON_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
