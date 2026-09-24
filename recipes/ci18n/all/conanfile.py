from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class Ci18nConan(ConanFile):
    name = "ci18n"
    description = ("Single-header C i18n library: translations, CLDR plural rules for 71 languages, "
                   "formatting, UTF-8 and right-to-left text.")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ilyabrin/ci18n"
    topics = ("i18n", "l10n", "localization", "translation", "pluralization", "cldr", "embedded", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "ci18n.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ci18n")
        self.cpp_info.set_property("cmake_target_name", "ci18n::ci18n")
        self.cpp_info.set_property("pkg_config_name", "ci18n")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
