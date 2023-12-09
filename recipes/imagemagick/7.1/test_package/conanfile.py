import json
import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        dependency_opts = {k: str(v) == "True" for k, v in self.dependencies["imagemagick"].options.items() if k.startswith("with_")}
        self.generators_path.joinpath("dependencies.json").write_text(json.dumps(dependency_opts, indent=2, sort_keys=True))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            dependency_opts = json.loads(self.generators_path.joinpath("dependencies.json").read_text())

            with open("delegates.txt") as f:
                content = f.read()

            def check(option, token):
                self.output.info(f"checking feature {token}...")
                if dependency_opts[option]:
                    if token not in content.split():
                        raise Exception(f"feature {token} wasn't enabled!")
                self.output.info(f"checking feature {token}... OK!")

            check("with_zlib", "zlib")
            check("with_bzlib", "bzlib")
            check("with_lzma", "lzma")
            check("with_lcms", "lcms")
            check("with_openexr", "openexr")
            check("with_heic", "heic")
            check("with_jbig", "jbig")
            check("with_jpeg", "jpeg")
            check("with_openjp2", "jp2")
            check("with_pango", "pangocairo")
            check("with_png", "png")
            check("with_tiff", "tiff")
            check("with_webp", "webp")
            check("with_freetype", "freetype")
            check("with_xml2", "xml")
