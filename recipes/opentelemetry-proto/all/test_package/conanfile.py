import os
from conans import ConanFile


class TestPackageConan(ConanFile):

    def test(self):
        res_folder = self.deps_user_info["opentelemetry-proto"].proto_root
        assert os.path.isfile(os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto"))
