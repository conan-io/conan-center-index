from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class JsonconsConan(ConanFile):
    name = "jsoncons"
    description = "A C++, header-only library for constructing JSON and JSON-like data formats, with JSON Pointer, JSON Patch, JSON Schema, JSONPath, JMESPath, CSV, MessagePack, CBOR, BSON, UBJSON"
    topics = ("json", "csv", "cpp", "json-serialization", "cbor", "json-parser", "messagepack", "json-pointer", "json-patch", "json-diff", "bson", "ubjson", "json-parsing", "jsonpath", "jmespath", "csv-parser", "csv-reader", "jsonschema", "json-construction", "streaming-json-read")
    homepage = "https://github.com/danielaparker/jsoncons"
    url = "https://github.com/danielaparker/jsoncons"
    author = "Daniel Parker danielaparker@yahoo.com"
    license = "Boost Software License"
    no_copy_source = True

    def layout(self):
        basic_layout(self)

    def source(self):
        get(
            f"https://github.com/danielaparker/jsoncons/archive/refs/tags/v{self.version}.tar.gz", 
            destination=self.source_folder,
            strip_root=True
        )

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jsoncons")
        self.cpp_info.set_property("cmake_target_name", "jsoncons")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "jsoncons"
        self.cpp_info.names["cmake_find_package_multi"] = "jsoncons"
