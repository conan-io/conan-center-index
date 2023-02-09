from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class ConfuJson(ConanFile):
    name = "confu_json"
    homepage = "https://github.com/werto87/confu_json"
    description = "uses boost::fusion to help with serialization; json <-> user defined type"
    topics = ("json parse", "serialization", "user defined type")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20" if Version(self.version) < "1.0.0" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "Visual Studio": "17",
                "msvc": "193",
                "gcc": "7",
                "clang": "7",
            },
            "20": {
                "Visual Studio": "17",
                "msvc": "193",
                "gcc": "10",
                "clang": "10",
            },
        }.get(self._min_cppstd, {})

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0")
        self.requires("magic_enum/0.8.2")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("apple-clang is not supported. Pull request welcome")

        if self.settings.compiler == "gcc" and Version(self.version) < "1.0.0":
            raise ConanInvalidConfiguration("gcc is only supported in versions greater than or equal 1.0.0.")

        if is_msvc(self) and Version(self.version) < "0.0.9":
            raise ConanInvalidConfiguration("Visual Studio is not supported in versions before confu_json/0.0.9")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h*", src=os.path.join(self.source_folder, "confu_json"),
                           dst=os.path.join(self.package_folder, "include", "confu_json"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
