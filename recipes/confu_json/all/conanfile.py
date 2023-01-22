from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class ConfuJson(ConanFile):
    name = "confu_json"
    description = "uses boost::fusion to help with serialization; json <-> user defined type"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/werto87/confu_json"
    topics = ("json parse", "serialization", "user defined type", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 20 if Version(self) < "1.0.0" else 17

    @property
    def _minimum_compilers_version(self):
        if Version(self) < "1.0.0":
            return {
                "Visual Studio": "17",
                "msvc": "193",
                "gcc": "10",
                "clang": "10",
            }
        else:
            return {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "8",
                "clang": "7",
            }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0")
        self.requires("magic_enum/0.8.2")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if is_msvc(self) and Version(self.version) < "0.0.9":
            raise ConanInvalidConfiguration(
                "Visual Studio is not supported in versions before confu_json/0.0.9")
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration(
                "apple-clang is not supported. Pull request welcome")
        
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.ref} recipe lacks information about the {self.settings.compiler} "
                             "compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hxx",
            dst=os.path.join(self.package_folder, "include", "confu_json"),
            src=os.path.join(self.source_folder, "confu_json"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
