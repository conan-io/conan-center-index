from conan import ConanFile
from conan.tools.build import can_run

import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _atlas_texture_file(self):
        return os.path.join(self.build_folder, "atlas_texture.png")

    @property
    def _atlas_desc_file(self):
        return os.path.join(self.build_folder, "atlas_desc.json")

    def test(self):
        if can_run(self):
            ttf_path = os.path.join(self.source_folder, "Sacramento-Regular.ttf")
            charset_path = os.path.join(self.source_folder, "uppercase_charset")

            ret_code = self.run(
                "msdf-atlas-gen -font {} -charset {} -imageout {} -json {}".format(ttf_path, charset_path, self._atlas_texture_file, self._atlas_desc_file), env="conanrun")

            assert ret_code == 0
            assert os.path.isfile(self._atlas_texture_file)
            assert os.path.isfile(self._atlas_desc_file)

