from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.1"

class ReflectCppConan(ConanFile):
    name = "reflect-cpp"
    description = "C++-20 library for fast serialization, deserialization and validation using reflection"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/getml/reflect-cpp"
    topics = ("reflection", "serialization", "memory", "json", "xml", "flatbuffers", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_json" : [True, False],
        "with_xml" : [True, False],
        "with_flatbuffers" : [True, False],
        "with_yaml": [True, False],
    }
    default_options = {
        "with_json" : False,
        "with_xml" : False,
        "with_flatbuffers" : False,
        "with_yaml" : False,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "11.4",
            "clang": "16",
            "apple-clang": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_json:
            self.requires("yyjson/0.8.0", transitive_headers=True)
        if self.options.with_xml:
            self.requires("pugixml/1.14", transitive_headers=True)
        if self.options.with_flatbuffers:
            self.requires("flatbuffers/23.5.26", transitive_headers=True)
        if self.options.with_yaml:
            self.requires("yaml-cpp/0.8.0", transitive_headers=True)
            
    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
