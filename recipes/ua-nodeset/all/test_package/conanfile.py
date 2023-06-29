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
            nodeset_dir = self.dependencies["ua-nodeset"].conf_info.get("user.ua-nodeset:nodeset_dir")
        else:
            # TODO: to remove in conan v2
            nodeset_dir = self.deps_user_info["ua-nodeset"].nodeset_dir

        test_path = os.path.join(nodeset_dir, "PLCopen")
        assert os.path.exists(test_path)
