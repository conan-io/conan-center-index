from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import rm
from conan.errors import ConanException
from os.path import exists


# It will become the standard on Conan 2.x
class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        pass

    def test(self):
        if not can_run(self):
            return
        
        output_file = "id_rsa"

        if exists(f"{output_file}"):
            rm(self, output_file, ".")

        self.run(f"ssh-keygen -t rsa -b 4096 -f {output_file} -N ''", env="conanrun")

        if not exists(f"{output_file}"):
            raise ConanException(f"{output_file} does not exist")
