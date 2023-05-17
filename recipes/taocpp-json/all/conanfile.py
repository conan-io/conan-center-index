from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class TaoCPPJSONConan(ConanFile):
    name = "taocpp-json"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/json"
    description = "C++ header-only JSON library"
    topics = ("json", "jaxn", "cbor", "msgpack",
              "ubjson", "json-pointer", "json-patch")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.0.0-beta.11" else "17"

    @property
    def _min_compilers_version(self):
        return {
            "17": {
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    @property
    def _requires_pegtl(self):
        return Version(self.version) >= "1.0.0-beta.13"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._requires_pegtl:
            self.requires("taocpp-pegtl/3.2.7")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        min_compiler_version = self._min_compilers_version.get(str(self.settings.compiler), False)
        if min_compiler_version and Version(self.settings.compiler.version) < min_compiler_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "taocpp-json")
        self.cpp_info.set_property("cmake_target_name", "taocpp::json")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["json"].bindirs = []
        self.cpp_info.components["json"].libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-json"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-json"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["json"].names["cmake_find_package"] = "json"
        self.cpp_info.components["json"].names["cmake_find_package_multi"] = "json"
        self.cpp_info.components["json"].set_property("cmake_target_name", "taocpp::json")
        if self._requires_pegtl:
            self.cpp_info.components["json"].requires = ["taocpp-pegtl::taocpp-pegtl"]
