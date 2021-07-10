import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.converters"
    license = "MIT"
    homepage = "https://github.com/linksplatform/Converters"
    url = "https://github.com/conan-io/conan-center-index"
    description = """lol"""
    topics = ("linksplatform", "cpp20", "converters", "header-only")
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Converters")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "11",
            "apple-clang": "11"
        }

    @property
    def _minimum_cpp_standard(self):
        return 20

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))

        if tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("platform.Converters/{} "
                                            "requires C++{} with {}, "
                                            "which is not supported "
                                            "by {} {}.".format(
                self.version, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler,
                self.settings.compiler.version))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._internal_cpp_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Platform.Converters"
        self.cpp_info.names["cmake_find_package_multi"] = "Platform.Converters"
