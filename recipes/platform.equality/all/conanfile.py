from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.equality"
    license = "LGPL-3.0-or-later"
    homepage = "https://github.com/linksplatform/Equality"
    url = "https://github.com/conan-io/conan-center-index"
    description = "platform.delegates is one of the libraries of the LinksPlatform modular framework, " \
        "which uses innovations from the C++20 standard, for slow parody any typing dictionary and others."
    topics = ("linksplatform", "cpp20", "equality", "ranges", "any", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Equality")

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

        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("platform.equality/{} "
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
