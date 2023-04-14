from conan import ConanFile
from conan.tools.files import get, copy, save
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class OpenTelemetryProtoConan(ConanFile):
    name = "opentelemetry-proto"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open-telemetry/opentelemetry-proto"
    description = "Protobuf definitions for the OpenTelemetry protocol (OTLP)"
    topics = ("opentelemetry", "telemetry", "otlp")
    package_type = "unknown"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.proto",
            dst=os.path.join(self.package_folder, "res"),
            src=self.source_folder,
        )
        # satisfy KB-H014 (header_only recipes require headers)
        save(self, os.path.join(self.package_folder, "include", "dummy_header.h"), "\n")

    def package_info(self):
        self.conf_info.define("user.myconf:proto_root", os.path.join(self.package_folder, "res"))
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.resdirs = []

        self.user_info.proto_root = os.path.join(self.package_folder, "res")
