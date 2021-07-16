import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class PlatformSettersConan(ConanFile):
    name = "platform.setters"
    license = "MIT"
    homepage = "https://github.com/linksplatform/Setters"
    url = "https://github.com/conan-io/conan-center-index"
    description = """LinksPlatform's Platform.Setters is a library that contains set of C++ class 
    templates. Each setter provides a set of callback methods to set the result value. Use Platform.Setters.h file 
    to include the library."""
    topics = ("linksplatform", "platform", "setters", "concepts", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Setters")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "11",
            "apple-clang": "11"
        }

    def requirements(self):
        self.requires("platform.interfaces/0.1.3")

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        if tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("platform.setters/{} "
                                            "requires C++20 with {}, "
                                            "which is not supported "
                                            "by {} {}.".format(self.version, self.settings.compiler, self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._internal_cpp_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
