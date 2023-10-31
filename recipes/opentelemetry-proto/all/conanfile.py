import os

from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class OpenTelemetryProtoConan(ConanFile):
    name = "opentelemetry-proto"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open-telemetry/opentelemetry-proto"
    description = "Protobuf definitions for the OpenTelemetry protocol (OTLP)"
    topics = ("opentelemetry", "telemetry", "otlp", "pre-built")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def build(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE",
             dst=os.path.join(self.package_folder, "licenses"), src=self.build_folder)
        copy(self, pattern="*.proto",
             dst=os.path.join(self.package_folder, "res"), src=self.build_folder)

    def package_info(self):
        self.conf_info.define("user.opentelemetry-proto:proto_root",
                              os.path.join(self.package_folder, "res"))
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # TODO: to remove in conan v2
        self.user_info.proto_root = os.path.join(self.package_folder, "res")
