from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.hashing"
    license = "LGPL-3.0-only"
    homepage = "https://github.com/linksplatform/Hashing"
    url = "https://github.com/conan-io/conan-center-index"
    description = "platform.hashing is one of the libraries of the LinksPlatform modular framework," \
                  "which contains std::hash specializations for:" \
                  "trivial and standard-layout types" \
                  "types constrained by std::ranges::range" \
                  "std::any"
    topics = ("linksplatform", "cpp20", "hashing", "any", "ranges", "native")
    settings = "compiler", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Hashing")

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
            raise ConanInvalidConfiguration("platform.Hashing/{} "
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
