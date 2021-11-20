from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.interfaces"
    license = "MIT"
    homepage = "https://github.com/linksplatform/Interfaces"
    url = "https://github.com/conan-io/conan-center-index"
    description = """platform.interfaces is one of the libraries of the LinksPlatform modular framework, which uses
    innovations from the C++20 standard, for easier use of static polymorphism. It also includes some auxiliary
    structures for more convenient work with containers."""
    topics = ("linksplatform", "cpp20", "interfaces", "concepts", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Interfaces")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            #"clang": "11",
            "apple-clang": "11"
        }

    @property
    def _minimum_cpp_standard(self):
        return 20

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not self.settings.compiler:
            raise ConanInvalidConfiguration("{}/{} requires {} compiler").format(
                self.name, self.version, self.settings.compiler)

        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires c++{}, "
                                            "which is not supported by {} {}.".format(
                self.name, self.version, self._minimum_cpp_standard, self.settings.compiler,
                self.settings.compiler.version))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*.h", dst="include", src=self._internal_cpp_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
