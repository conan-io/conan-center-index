from conans import ConanFile, CMake, tools
import os


class TestUaNodeSetConan(ConanFile):

    def build(self):
        pass

    def test(self):
        assert os.path.exists(os.path.join(self.deps_user_info["ua-nodeset"].nodeset_dir, "PLCopen"))

