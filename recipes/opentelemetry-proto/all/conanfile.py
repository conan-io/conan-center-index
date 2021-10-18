import os
from pathlib import Path
from conans import ConanFile, tools


required_conan_version = ">=1.33.0"


class OpenTelemetryProtoConan(ConanFile):
    name = "opentelemetry-proto"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/open-telemetry/opentelemetry-proto"
    description = "Protobuf definitions for the OpenTelemetry protocol (OTLP)"
    topics = ("opentelemetry", "telemetry", "otlp")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder,
                  strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.proto", dst="res", src=self._source_subfolder)

    def package_info(self):
        self.user_info.proto_root = os.path.join(self.package_folder, "res")
