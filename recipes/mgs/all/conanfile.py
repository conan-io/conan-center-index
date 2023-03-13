from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class MgsConan(ConanFile):
    name = "mgs"
    description = "C++14 codec library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://theodelrieu.github.io/mgs-docs"
    topics = ("codec", "base64", "base32", "base16", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "msvc": "190",
            "clang": "3.4",
            "apple-clang": "3.4",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not fully support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mgs")

        self.cpp_info.components["mgs-config"].set_property("cmake_target_name", "mgs::config")

        self.cpp_info.components["mgs-meta"].set_property("cmake_target_name", "mgs::meta")
        self.cpp_info.components["mgs-meta"].requires = ["mgs-config"]

        self.cpp_info.components["mgs-exceptions"].set_property("cmake_target_name", "mgs::exceptions")
        self.cpp_info.components["mgs-exceptions"].requires = ["mgs-config"]

        self.cpp_info.components["mgs-codecs"].set_property("cmake_target_name", "mgs::codecs")
        self.cpp_info.components["mgs-codecs"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions"]

        self.cpp_info.components["mgs-base_n"].set_property("cmake_target_name", "mgs::base_n")
        self.cpp_info.components["mgs-base_n"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs"]

        self.cpp_info.components["mgs-base16"].set_property("cmake_target_name", "mgs::base16")
        self.cpp_info.components["mgs-base16"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base32"].set_property("cmake_target_name", "mgs::base32")
        self.cpp_info.components["mgs-base32"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base64"].set_property("cmake_target_name", "mgs::base64")
        self.cpp_info.components["mgs-base64"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base64url"].set_property("cmake_target_name", "mgs::base64url")
        self.cpp_info.components["mgs-base64url"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base32hex"].set_property("cmake_target_name", "mgs::base32hex")
        self.cpp_info.components["mgs-base32hex"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "mgs"
        self.cpp_info.names["cmake_find_package_multi"] = "mgs"

        self.cpp_info.components["mgs-config"].names["cmake_find_package"] = "config"
        self.cpp_info.components["mgs-config"].names["cmake_find_package_multi"] = "config"

        self.cpp_info.components["mgs-meta"].names["cmake_find_package"] = "meta"
        self.cpp_info.components["mgs-meta"].names["cmake_find_package"] = "meta"

        self.cpp_info.components["mgs-exceptions"].names["cmake_find_package"] = "exceptions"
        self.cpp_info.components["mgs-exceptions"].names["cmake_find_package_multi"] = "exceptions"

        self.cpp_info.components["mgs-codecs"].names["cmake_find_package"] = "codecs"
        self.cpp_info.components["mgs-codecs"].names["cmake_find_package_multi"] = "codecs"

        self.cpp_info.components["mgs-base_n"].names["cmake_find_package"] = "base_n"
        self.cpp_info.components["mgs-base_n"].names["cmake_find_package_multi"] = "base_n"

        self.cpp_info.components["mgs-base16"].names["cmake_find_package"] = "base16"
        self.cpp_info.components["mgs-base16"].names["cmake_find_package_multi"] = "base16"

        self.cpp_info.components["mgs-base32"].names["cmake_find_package"] = "base32"
        self.cpp_info.components["mgs-base32"].names["cmake_find_package_multi"] = "base32"

        self.cpp_info.components["mgs-base64"].names["cmake_find_package"] = "base64"
        self.cpp_info.components["mgs-base64"].names["cmake_find_package_multi"] = "base64"

        self.cpp_info.components["mgs-base64url"].names["cmake_find_package"] = "base64url"
        self.cpp_info.components["mgs-base64url"].names["cmake_find_package_multi"] = "base64url"

        self.cpp_info.components["mgs-base32hex"].names["cmake_find_package"] = "base32hex"
        self.cpp_info.components["mgs-base32hex"].names["cmake_find_package_multi"] = "base32hex"
