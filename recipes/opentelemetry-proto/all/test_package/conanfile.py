import os

from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        pass

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        res_folder = self.dependencies[self.tested_reference_str].conf_info.get("user.opentelemetry-proto:proto_root")
        proto_path = os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto")
        assert os.path.isfile(proto_path)
