import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


required_conan_version = ">=1.51.3"


class TomlPlusPlusConan(ConanFile):
    name = "tomlplusplus"
    description = "Header-only TOML config file parser and serializer for modern C++."
    topics = ("tomlformoderncpp", "tomlcpp", "toml", "json", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/marzer/tomlplusplus"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "exceptions": [True, False, None]
    }
    default_options = {
        "exceptions": None
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16" if Version(self.version) < "2.2.0" or Version(self.version) >= "3.0.0" else "15",
            "msvc": "192" if Version(self.version) < "2.2.0" or Version(self.version) >= "3.0.0" else "191",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.compiler == "apple-clang" and Version(self.version) < "2.3.0":
            raise ConanInvalidConfiguration("apple-clang is not supported in versions < 2.3.0")

        if is_msvc(self) and Version(self.version) == "2.1.0":
            raise ConanInvalidConfiguration("msvc is unable to build version 2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h**", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="toml.hpp", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tomlplusplus")
        self.cpp_info.set_property("cmake_target_name", "tomlplusplus::tomlplusplus")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Casting as a String because None value would not be properly handled, this is a PackageOption, not the value itself
        # which `is` never None
        if str(self.options.exceptions) != "None":
            define_value = "1" if self.options.exceptions is True else "0"
            self.cpp_info.defines.append(f"TOML_EXCEPTIONS={define_value}")
