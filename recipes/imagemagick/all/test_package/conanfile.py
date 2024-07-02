from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os

from conan.tools.files import save, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        opts = self.dependencies["imagemagick"].options
        delegates = [
            (opts.with_zlib, "zlib"),
            (opts.with_bzlib, "bzlib"),
            (opts.with_lzma, "lzma"),
            (opts.with_lcms, "lcms"),
            (opts.with_openexr, "openexr"),
            (opts.with_heic, "heic"),
            (opts.with_jbig, "jbig"),
            (opts.with_jpeg, "jpeg"),
            (opts.with_openjp2, "jp2"),
            (opts.with_pango, "pangocairo"),
            (opts.with_png, "png"),
            (opts.with_tiff, "tiff"),
            (opts.with_webp, "webp"),
            (opts.with_freetype, "freetype"),
            (opts.with_xml2, "xml"),
            (opts.with_djvu, "djvu"),
        ]
        enabled = []
        disabled = []
        for option, delegate in delegates:
            if option:
                enabled.append(delegate)
            else:
                disabled.append(delegate)
        save(self, os.path.join(self.generators_folder, "enabled"), " ".join(enabled))
        save(self, os.path.join(self.generators_folder, "disabled"), " ".join(disabled))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            delegates = set(load(self, "delegates.txt").strip().split())
            expect_enabled = set(load(self, os.path.join(self.generators_folder, "enabled")).strip().split())
            expect_disabled = set(load(self, os.path.join(self.generators_folder, "disabled")).strip().split())

            if expect_enabled - delegates:
                raise Exception("Some expected image formats are missing: " + " ".join(expect_enabled - delegates))
            if expect_disabled & delegates:
                raise Exception("Some unexpected image formats are available: " + " ".join(expect_disabled & delegates))

            print("All expected image formats are available")
