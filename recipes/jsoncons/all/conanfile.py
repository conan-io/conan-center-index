from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class JsonconsConan(ConanFile):
    name = "jsoncons"
    description = "A C++, header-only library for constructing JSON and JSON-like data formats, with JSON Pointer, JSON Patch, JSON Schema, JSONPath, JMESPath, CSV, MessagePack, CBOR, BSON, UBJSON"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danielaparker/jsoncons"
    topics = (
        "json", "csv", "json-serialization", "cbor", "json-parser",
        "messagepack", "json-pointer", "json-patch", "json-diff", "bson",
        "ubjson", "json-parsing", "jsonpath", "jmespath", "csv-parser",
        "csv-reader", "jsonschema", "json-construction", "streaming-json-read",
        "header-only",
    )
    pckage_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "0.172.0" else "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "gcc": "6",
                "clang": "5",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "jsoncons")
        self.cpp_info.set_property("cmake_target_name", "jsoncons")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "jsoncons"
        self.cpp_info.names["cmake_find_package_multi"] = "jsoncons"
