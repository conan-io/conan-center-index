import hashlib
import os
import shutil

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.files import chdir


def sha256sum(file_path):
    with open(file_path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("lzip --version")

            os.mkdir("build")
            with chdir(self, "build"):
                shutil.copy(os.path.join(self.source_folder, "conanfile.py"), "conanfile.py")

                sha256_original = sha256sum("conanfile.py")
                self.run("lzip conanfile.py")
                if not os.path.exists("conanfile.py.lz"):
                    raise ConanException("conanfile.py.lz does not exist")
                if os.path.exists("conanfile.py"):
                    raise ConanException("copied conanfile.py should not exist anymore")

                self.run("lzip -d conanfile.py.lz")
                if sha256sum("conanfile.py") != sha256_original:
                    raise ConanException("sha256 from extracted conanfile.py does not match original")
