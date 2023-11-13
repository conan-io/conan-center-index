from conans import ConanFile, CMake
import os

class TestPackageV1Conan(ConanFile):
    def test(self):
        res_folder = self.deps_user_info["opentelemetry-proto"].proto_root
        assert os.path.isfile(os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto"))
