from conan import ConanFile
from conan.tools.cmake import CMakeToolchain
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


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
    def _internal_cpp_subfolder(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Converters")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "14",
            "apple-clang": "14"
        }

    @property
    def _minimum_cpp_standard(self):
        return 20

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))

        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires c++{}, "
                                            "which is not supported by {} {}.".format(
                self.ref, self._minimum_cpp_standard, self.settings.compiler,
                self.settings.compiler.version))

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)

    def package(self):
        copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=self.source_folder,
            )
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)
    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "Platform.Converters")
        self.cpp_info.set_property("cmake_target_name", "Platform.Converters::Platform.Converters")
        self.cpp_info.set_property("cmake_file_name", "Platform.Converters")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Platform.Converters"
        self.cpp_info.names["cmake_find_package_multi"] = "Platform.Converters"
