from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import save, load
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        build_vars = self.dependencies[self.tested_reference_str].buildenv_info.vars(self, scope="build")
        mpc_root = build_vars["MPC_ROOT"]
        save(self, os.path.join(self.build_folder, "mpc_root.txt"), mpc_root)

    def test(self):
        mpc_root = load(self, os.path.join(self.build_folder, "mpc_root.txt"))
        assert os.path.exists(os.path.join(mpc_root, 'mpc.pl'))
