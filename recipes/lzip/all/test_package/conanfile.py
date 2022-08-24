from conans import ConanFile, tools
from conans.errors import ConanException
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.build.cross_building(self, self, skip_x64_x86=True):
            lzip = os.path.join(self.deps_cpp_info["lzip"].bin_paths[0], "lzip")
            self.run("{} --version".format(lzip))

            shutil.copy(os.path.join(self.source_folder, "conanfile.py"),
                        "conanfile.py")

            sha256_original = tools.sha256sum("conanfile.py")
            self.run("{} conanfile.py".format(lzip), run_environment=True)
            if not os.path.exists("conanfile.py.lz"):
                raise ConanException("conanfile.py.lz does not exist")
            if os.path.exists("conanfile.py"):
                raise ConanException("copied conanfile.py should not exist anymore")

            self.run("{} -d conanfile.py.lz".format(lzip), run_environment=True)
            if tools.sha256sum("conanfile.py") != sha256_original:
                raise ConanException("sha256 from extracted conanfile.py does not match original")
