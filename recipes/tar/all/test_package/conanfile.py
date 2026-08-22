import os

from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.files import chdir, load, save


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def generate(self):
        tar_bin = self.dependencies.build["tar"].conf_info.get("user.tar:path")
        save(self, os.path.join(self.build_folder, "tar_bin"), tar_bin)

    def test(self):
        # Verify that the compression tools are available
        self.run("gzip --version")
        self.run("bzip2 --help")
        self.run("lzip --version")
        self.run("lzma --version")
        self.run("zstd --version")

        tar_bin = load(self, os.path.join(self.build_folder, "tar_bin"))
        with chdir(self, self.source_folder):
            test_tar = os.path.join(self.build_folder, "test.tar.zstd")
            self.run(f"{tar_bin} --zstd -cf {test_tar} conanfile.py")
        assert os.path.isfile("test.tar.zstd")
        self.run(f"{tar_bin} -tf test.tar.zstd")
        self.run(f"{tar_bin} -xf test.tar.zstd")
        f1 = load(self, os.path.join(self.source_folder, "conanfile.py"))
        f2 = load(self, os.path.join(self.build_folder, "conanfile.py"))
        assert f1 == f2
