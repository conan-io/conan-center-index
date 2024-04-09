import os

from conan import ConanFile
from conan.tools.files import save, load
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        save(self, os.path.join(self.build_folder, "proto_root"), self.dependencies["opentelemetry-proto"].conf_info.get("user.opentelemetry-proto:proto_root"))

    def test(self):
        res_folder = load(self, os.path.join(self.build_folder, "proto_root"))
        proto_path = os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto")
        assert os.path.isfile(proto_path)
