import gzip
import os
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import save
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        pigz = self.dependencies["pigz"]
        bindir = os.path.join(pigz.package_folder, "bin")
        for name in ("unpigz", "gzip", "gunzip", "zcat"):
            path = os.path.join(bindir, name)
            if name == "unpigz" or pigz.options.install_symlinks:
                assert os.path.islink(path), f"Missing symlink: {name}"
                assert os.readlink(path) == "pigz"
                assert os.path.isfile(path), f"Broken symlink: {name}"
            else:
                assert not os.path.lexists(path), f"Unexpected alias: {name}"

        if can_run(self):
            self.run(f'"{bindir}/pigz" --version', env="conanrun")
            payload = "pigz package test\n" * 1000
            save(self, "input.txt", payload)
            commands = [("pigz", "unpigz")]
            if pigz.options.install_symlinks:
                commands.extend([("gzip", "gunzip"), ("gzip", "zcat")])
            for compressor, decompressor in commands:
                self.run(f'"{bindir}/{compressor}" -c input.txt > compressed.gz', env="conanrun")
                assert gzip.decompress(Path("compressed.gz").read_bytes()) == payload.encode()
                self.run(f'"{bindir}/{decompressor}" -c compressed.gz > output.txt', env="conanrun")
                assert Path("output.txt").read_bytes() == payload.encode()
