import os

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.interfaces"
    license = "Unlicense"
    homepage = "https://github.com/linksplatform/Interfaces"
    url = "https://github.com/conan-io/conan-center-index"
    description = """platform.interfaces is one of the libraries of the LinksPlatform modular framework, which uses
    innovations from the C++20 standard, for easier use of static polymorphism. It also includes some auxiliary
    structures for more convenient work with containers."""
    topics = ("platform", "concepts", "header-only")
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _subfolder_sources(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Interfaces")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "11",
            "apple-clang": "11"
        }

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("platform.interfaces/{} "
                                            "requires C++20 with {}, "
                                            "which is not supported "
                                            "by {} {}.".format(self.version, self.settings.compiler, self.settings.compiler, self.settings.compiler.version))
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 20)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("*.h", dst="include", src=self._subfolder_sources)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Platform.Interfaces"
        self.cpp_info.names["cmake_find_package_multi"] = "Platform.Interfaces"
