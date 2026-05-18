from conan import ConanFile
from conan.tools.env import VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        env_vars = VirtualRunEnv(self).environment().vars(self, scope="run")
        vk_layer_path = env_vars.get("VK_LAYER_PATH")
        assert vk_layer_path, "VK_LAYER_PATH is not set in the conanrun environment"
        self.output.info(f"VK_LAYER_PATH = {vk_layer_path}")
