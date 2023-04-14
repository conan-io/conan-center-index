from conan import ConanFile
from conan.tools.layout import basic_layout
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        res_folder = self.dependencies["opentelemetry-proto"].conf_info.get("user.opentelemetry-proto:proto_root")
        assert os.path.isfile(os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto"))
