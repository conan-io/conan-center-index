import os

from conan import ConanFile, conan_version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        pass

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if conan_version.major >= 2:
            res_folder = self.dependencies["opentelemetry-proto"].conf_info.get("user.opentelemetry-proto:proto_root")
        else:
            # TODO: to remove in conan v2
            res_folder = self.deps_user_info["opentelemetry-proto"].proto_root

        proto_path = os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto")
        assert os.path.isfile(proto_path)
