from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            with open("delegates.txt") as f:
                content = f.read()

            def check(option, token):
                self.output.info(f"checking feature {token}...")
                if option:
                    if token not in content.split():
                        raise Exception(f"feature {token} wasn't enabled!")
                self.output.info(f"checking feature {token}... OK!")

            opts = self.dependencies["imagemagick"].options
            check(opts.with_zlib, "zlib")
            check(opts.with_bzlib, "bzlib")
            check(opts.with_lzma, "lzma")
            check(opts.with_lcms, "lcms")
            check(opts.with_openexr, "openexr")
            check(opts.with_heic, "heic")
            check(opts.with_jbig, "jbig")
            check(opts.with_jpeg, "jpeg")
            check(opts.with_openjp2, "jp2")
            check(opts.with_pango, "pangocairo")
            check(opts.with_png, "png")
            check(opts.with_tiff, "tiff")
            check(opts.with_webp, "webp")
            check(opts.with_freetype, "freetype")
            check(opts.with_xml2, "xml")
