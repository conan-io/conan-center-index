import bz2
import os
from pathlib import Path

from conan import ConanFile
from conan.tools.build import can_run
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
        lbzip2 = self.dependencies["lbzip2"]
        bindir = os.path.join(lbzip2.package_folder, "bin")
        for name in ("lbunzip2", "lbzcat", "bzip2", "bunzip2", "bzcat"):
            path = os.path.join(bindir, name)
            if name in ("lbunzip2", "lbzcat") or lbzip2.options.install_symlinks:
                assert os.path.islink(path), f"Missing symlink: {name}"
                assert os.readlink(path) == "lbzip2"
                assert os.path.isfile(path), f"Broken symlink: {name}"
            else:
                assert not os.path.lexists(path), f"Unexpected alias: {name}"

        if can_run(self):
            self.run(f'"{bindir}/lbzip2" --version', env="conanrun")
            commands = [("lbzip2", "lbunzip2"), ("lbzip2", "lbzcat")]
            if lbzip2.options.install_symlinks:
                commands.extend([("bzip2", "bunzip2"), ("bzip2", "bzcat")])
            for payload in (b"", bytes(range(256)) * 100):
                Path("input.bin").write_bytes(payload)
                for compressor, decompressor in commands:
                    self.run(f'"{bindir}/{compressor}" -n 2 -c input.bin > compressed.bz2', env="conanrun")
                    assert bz2.decompress(Path("compressed.bz2").read_bytes()) == payload
                    Path("compressed.bz2").write_bytes(bz2.compress(payload))
                    self.run(f'"{bindir}/{decompressor}" -n 2 -c compressed.bz2 > output.bin', env="conanrun")
                    assert Path("output.bin").read_bytes() == payload
