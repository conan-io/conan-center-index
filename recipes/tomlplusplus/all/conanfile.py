from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.51.3"


class TomlPlusPlusConan(ConanFile):
    name = "tomlplusplus"
    description = "Header-only TOML config file parser and serializer for modern C++."
    topics = ("tomlformoderncpp", "tomlcpp", "toml", "json", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/marzer/tomlplusplus"
    license = "MIT"
    settings = ("compiler", "arch", "os", "build_type")
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16" if Version(self.version) < "2.2.0" or Version(self.version) >= "3.0.0" else "15",
            "msvc": "1913",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        compiler = f"{self.settings.compiler} {self.settings.compiler.version}"
        if not min_version:
            self.output.warn(f"{self.ref} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires c++{self._minimum_cpp_standard} support."
                        " The current compiler {compiler} does not support it.")

        if self.settings.compiler == "apple-clang" and Version(self.version) < "2.3.0":
            raise ConanInvalidConfiguration(f"The compiler {compiler} is supported in version >= 2.3.0")

        if is_msvc(self) and Version(self.version) == "2.1.0":
            raise ConanInvalidConfiguration(f"The current compiler {compiler} is unable to build version 2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h**", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="toml.hpp", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        self.cpp_info.set_property("cmake_file_name", "tomlplusplus")
        self.cpp_info.set_property("cmake_target_name", "tomlplusplus::tomlplusplus")
