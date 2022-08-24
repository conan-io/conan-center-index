from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PlatformConvertersConan(ConanFile):
    name = "platform.converters"
    license = "MIT"
    homepage = "https://github.com/linksplatform/Converters"
    url = "https://github.com/conan-io/conan-center-index"
    description = "platform.converters is one of the libraries of the LinksPlatform modular framework, " \
                  "to provide conversions between different types"
    topics = ("linksplatform", "cpp20", "converters", "any", "native")
    settings = "compiler", "arch"
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
            "clang": "14",
            "apple-clang": "14"
        }

    @property
    def _minimum_cpp_standard(self):
        return 20

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))

        elif tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires c++{}, "
                                            "which is not supported by {} {}.".format(
                self.name, self.version, self._minimum_cpp_standard, self.settings.compiler,
                self.settings.compiler.version))

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.h", dst="include", src=self._internal_cpp_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
