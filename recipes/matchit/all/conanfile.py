from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class MatchitConan(ConanFile):
    name = "matchit"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BowenFu/matchit.cpp"
    license = "Apache-2.0"
    description = ("match(it): A lightweight header-only pattern-matching"
                   " library for C++17 with macro-free APIs.")
    topics = (
        "conan",
        "matchit",
        "cpp17",
        "header-only",
    )
    no_copy_source = True
    settings = "compiler"

    _compiler_required_cpp17 = {
        "Visual Studio": "16",
        "gcc": "8",
        "clang": "7",
        "apple-clang": "12.0",
    }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

        minimum_version = self._compiler_required_cpp17.get(
            str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn(
                "{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True,
            destination=self.source_folder)

    def build(self):
        pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "matchit.h",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "matchit"
        self.cpp_info.names["cmake_find_package_multi"] = "matchit"
